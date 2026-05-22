from pathlib import Path
import hashlib
import io
import requests
import itertools
from PIL import Image
import pandas as pd
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

TIMEOUT = 20
NUMBER_OF_THREADS = 64

class PersistentImageCache:
    def __init__(self, cache_dir="image_cache"):
        BASE_DIR = Path(__file__).resolve().parent.parent.parent
        valid_scocks5_path = BASE_DIR / "src" / "crawler" / "valid_socks5.txt"
        with open(valid_scocks5_path, "r") as f:
            proxy_list = [
                {
                    "http": f"{line.strip()}",
                    "https": f"{line.strip()}",
                }
                for line in f
                if line.strip()
            ]
        self.cache_dir = BASE_DIR / Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.mem = {}
        self.proxy_gen = itertools.cycle(proxy_list)

    def _key(self, url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()

    def _path(self, url: str) -> Path:
        return self.cache_dir / f"{self._key(url)}.img"

    def get(self, url: str) -> Image.Image:
        if url in self.mem:
            return self.mem[url]

        path = self._path(url)

        if path.exists():
            with path.open("rb") as f:
                img = Image.open(f).convert("RGB")
                img.load()
        else:
            r = requests.get(url, stream=True, proxies=next(self.proxy_gen), timeout=TIMEOUT)
            r.raise_for_status()
            img = Image.open(io.BytesIO(r.content)).convert("RGB")
            img.save(path, format="PNG")

        self.mem[url] = img
        return img

def download_df_images(
    df: pd.DataFrame,
    url_col="url_o",
    cache_dir="flickr_commons",
):
    cache = PersistentImageCache(cache_dir)
    urls = df[url_col].dropna().astype(str).unique().tolist()
    def worker(url):
        try:
            cache.get(url)
            return True
        except Exception:
            return False

    with ThreadPoolExecutor(max_workers=NUMBER_OF_THREADS) as executor:
        futures = [executor.submit(worker, url) for url in urls]

        for _ in tqdm(
            as_completed(futures),
            total=len(futures),
            desc="Downloading images",
        ):
            pass
    return df, cache


if __name__ == "__main__":
    pass
    # cache = PersistentImageCache("test_cache")
