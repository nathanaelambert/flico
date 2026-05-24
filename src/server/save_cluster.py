import pandas as pd
from .db import photo_to_group

def save():
    df = photo_to_group()
    df.to_csv('ghassan_731_clusters.csv', index=False)

if __name__== "__main__":
    save()