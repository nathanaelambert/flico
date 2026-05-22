from src.trainer.db import photo_relevant_geo
from src.crawler import PersistentImageCache
import pandas as pd
import time

cache = PersistentImageCache("test_cache")
df = photo_relevant_geo()

url_1 = 'https://live.staticflickr.com/2027/1906652073_7ab84b0e8a_o.jpg'
url_2 = 'https://live.staticflickr.com/2204/2162645323_6a56c91cfc_o.jpg'

start = time.perf_counter()
cache.get(url_1)
print("First fetch:", time.perf_counter() - start)

start = time.perf_counter()
cache.get(url_1)
print("Cached fetch:", time.perf_counter() - start)

"""
It works (when run a second time it seems to be using the disk read yay)
(.venv) n@pop-os:~/MA4/flico$ python -m test.img_cache
First fetch: 12.273825837000913
Cached fetch: 2.785299875540659e-05
(.venv) n@pop-os:~/MA4/flico$ python -m test.img_cache
First fetch: 0.00791377999848919
Cached fetch: 1.2590026017278433e-06
"""