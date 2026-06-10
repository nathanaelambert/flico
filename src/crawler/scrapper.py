import requests
import itertools
import os
from pathlib import Path
from tqdm import tqdm

"""
proxy list from https://github.com/TheSpeedX/PROXY-List/blob/master/socks5.txt
"""
def filter_valid_proxies():
    BASE_DIR = Path(__file__).resolve().parent
    socks5_path = BASE_DIR / "new_proxies.txt" 
    valid_scocks5_path = BASE_DIR / "new_valid_proxies.txt"


    with open(socks5_path, "r") as f:
        proxy_list = [
            {
                "http": f"{line.strip()}",
                "https": f"{line.strip()}",
            }
            for line in f
            if line.strip()
        ]

    proxy_gen = itertools.cycle(proxy_list)

    valid_proxies = []

    with tqdm(total=len(proxy_list), desc="Proxy sorting", unit="proxy") as pbar:
        for _ in range(len(proxy_list)):
            proxy = next(proxy_gen)
            proxy_str = proxy["http"]
            
            try:
                response = requests.get(
                    "https://httpbin.io/ip",
                    proxies=proxy,
                    timeout=10            )
                if response.status_code == 200:
                    valid_proxies.append(proxy_str)
                    with open(valid_scocks5_path, "a") as f:
                        f.write(proxy_str + "\n")
            except requests.RequestException:
                pass
            pbar.update(1)


if __name__ == "__main__": 
    filter_valid_proxies()