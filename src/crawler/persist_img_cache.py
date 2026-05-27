from pathlib import Path
import hashlib
import io
import requests
from PIL import Image
import random
import pandas as pd
import time
import threading
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
import json

CONNECTION_TIMEOUT = 5
READ_TIMEOUT = 8
MAX_TIME_PER_URL = 30
NUMBER_OF_THREADS = 64
RETRIES = 2

class Proxy:
    address: str
    last_2_time: float

class PersistentImageCache:
    def __init__(self, cache_dir="image_cache"):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        valid_scocks5_path = BASE_DIR / "src" / "crawler" / "valid_socks5.txt"
        proxy_scores_path =  BASE_DIR / "src" / "crawler" / "proxies_with_scores.json"
        self.proxy_scores_path = proxy_scores_path
        if proxy_scores_path.exists():
            with open(proxy_scores_path, "r") as f:
                raw_proxy_dict = json.load(f)
            self.proxy_dict = {
                tuple(sorted({"http": proxy,"https": proxy,}.items())): score
                for proxy, score in raw_proxy_dict.items()
            }
        else:
            with open(valid_scocks5_path, "r") as f:
                proxy_list = [
                    {
                        "http": f"{line.strip()}",
                        "https": f"{line.strip()}",
                    }
                    for line in f
                    if line.strip()
                ]
            self.proxy_dict = {
                tuple(sorted(proxy.items())): 0
                for proxy in proxy_list
            }
        self.cache_dir = BASE_DIR / Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.mem = OrderedDict()
        self.mem_size_bytes = 0
        self.max_mem_bytes = 10 * 1024**3  # 20 GB
        self.mem_lock = threading.Lock()

        self.proxy_lock = threading.Lock()

    def _key(self, url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def clear_ram(self):
        self.mem = OrderedDict()

    def _path(self, url: str) -> Path:
        return self.cache_dir / f"{self._key(url)}.img"

    def _choose_proxy(self):
        with self.proxy_lock:
            min_score = min(self.proxy_dict.values())

            candidates = [
                dict(proxy_tuple)
                for proxy_tuple, score in self.proxy_dict.items()
                if score == min_score
            ]

        return random.choice(candidates)

    def _increase_proxy_score(self, proxy, amount=1):
        key = tuple(sorted(proxy.items()))

        with self.proxy_lock:
            self.proxy_dict[key] += amount

    def _decrease_proxy_score(self, proxy, amount=1):
        key = tuple(sorted(proxy.items()))

        with self.proxy_lock:
            self.proxy_dict[key] = max(
                0,
                self.proxy_dict[key] - amount
            )

    def _estimate_image_size(self, img: Image.Image) -> int:
        bands = len(img.getbands())  # RGB -> 3
        return img.width * img.height * bands


    def _mem_get(self, url: str):
        with self.mem_lock:
            if url not in self.mem:
                return None

            img, size = self.mem.pop(url)

            # move to end (LRU)
            self.mem[url] = (img, size)

            return img


    def _mem_put(self, url: str, img: Image.Image):
        size = self._estimate_image_size(img)

        with self.mem_lock:

            # replace existing
            if url in self.mem:
                _, old_size = self.mem.pop(url)
                self.mem_size_bytes -= old_size

            self.mem[url] = (img, size)
            self.mem_size_bytes += size

            # evict LRU
            while self.mem_size_bytes > self.max_mem_bytes:
                _, (_, evicted_size) = self.mem.popitem(last=False)
                self.mem_size_bytes -= evicted_size
    
    def save_proxy_scores(self):
        with self.proxy_lock:
            serializable = {
                dict(proxy_tuple)["http"]: score
                for proxy_tuple, score in self.proxy_dict.items()
            }
        tmp_path = self.proxy_scores_path.with_suffix(".tmp")
        with open(tmp_path, "w") as f:
            json.dump(serializable, f, indent=2)
        tmp_path.replace(self.proxy_scores_path)

    def get(self, url: str,*, download_missing=False, fast_cache=False, disk_save=False) -> Image.Image:
        cached = self._mem_get(url)

        if cached is not None:
            return cached

        path = self._path(url)

        if path.exists():
            with path.open("rb") as f:
                img = Image.open(f).convert("RGB")
                img.load()

        else:
            if not download_missing:
                raise KeyError(f"cache miss: {url}")
                return None
            start = time.monotonic()
            for _ in range(RETRIES):
                if time.monotonic() - start > MAX_TIME_PER_URL:
                    raise TimeoutError("global timeout exceeded")
                proxy = self._choose_proxy()
                try:
                    r = requests.get(url, proxies=proxy, timeout=(CONNECTION_TIMEOUT, READ_TIMEOUT,),)
                    r.raise_for_status()

                    img = Image.open(io.BytesIO(r.content))
                    img.load()
                    img = img.convert("RGB")
                    if disk_save:
                        img.save(path, format="PNG")

                    # reward successful proxy
                    self._decrease_proxy_score(proxy)

                    break

                except requests.Timeout as e:
                    self._increase_proxy_score(proxy, amount=15)

                except requests.RequestException as e:
                    self._increase_proxy_score(proxy, amount=1)

                except TimeoutError as e:
                    self._increase_proxy_score(proxy, amount=25)

                except Exception as e:
                    self._increase_proxy_score(proxy, amount=2)
        if fast_cache:
            self._mem_put(url, img)
        return img

    def get_images(self, urls: list[str], download_missing=False, fast_cache=False, disk_save=False):
        imgs = [None] * len(urls)

        def worker(i, url):
            try:
                img = self.get(
                    url,
                    download_missing=download_missing,
                    fast_cache=fast_cache,
                    disk_save=disk_save,
                )
                return i, img
            except Exception:
                return i, None

        with ThreadPoolExecutor(max_workers=NUMBER_OF_THREADS) as executor:
            futures = [
                executor.submit(worker, i, url)
                for i, url in enumerate(urls)
            ]

            for future in tqdm(
                as_completed(futures),
                total=len(futures),
                desc=(
                    "Downloading images"
                    if download_missing
                    else "Retrieving images from disk"
                ),
            ):
                i, img = future.result()
                imgs[i] = img

        self.save_proxy_scores()

        return imgs


def download_df_images(df, cache, url_col="url_o", download_missing=False, fast_cache=False, disk_save=False):
        urls = df[url_col].dropna().astype(str).unique().tolist()
        def worker(url):
            try:
                cache.get(url, download_missing=download_missing, fast_cache=fast_cache, disk_save=disk_save)
                return True
            except Exception:
                return False
        successful_urls = set()
        with ThreadPoolExecutor(max_workers=NUMBER_OF_THREADS) as executor:
            future_to_url = {
                executor.submit(worker, url): url
                for url in urls
            }
            for future in tqdm(
                as_completed(future_to_url),
                total=len(future_to_url),
                desc=("Downloading images" if download_missing else "Retrieving images from disk"),
            ):
                url = future_to_url[future]
                try:
                    success = future.result()
                    if success:
                        successful_urls.add(url)
                except Exception:
                    pass
        cache.save_proxy_scores()
        filtered_df = df[df[url_col].astype(str).isin(successful_urls)].copy()
        return filtered_df
    


if __name__ == "__main__":
    pass
    # cache = PersistentImageCache("test_cache")
