import pandas as pd
from .db import photo_to_group
from ..core.db import get_photos_where

def save_cluster():
    df = photo_to_group()
    df.to_csv('ghassan_731_clusters.csv', index=False)

def save_matches():
    df = get_photos_where(user="server", clause="""--sql
    WHERE p_match is not null""")
    df.to_csv('karim_600_matches.csv', index=False)

if __name__== "__main__":
    # save_cluster()
    save_matches()