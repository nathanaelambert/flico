import pandas as pd

def filter(photos: pd.DataFrame) -> pd.DataFrame:
    """Only keep rows for the pictures wanted for geo analysis"""
    photos = photos[photos['accuracy'] != 0]
    return photos[['owner_nsid', 'id']]
