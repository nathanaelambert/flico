from src.crawler.main import get_stats
from src.server.db import count_date
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)


# view what is downloaded from flickr (slow (pings flickr))
# print(get_stats())

# count pictures with date
print(count_date())