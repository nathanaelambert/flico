import pandas as pd

def filter(photos: pd.DataFrame) -> pd.DataFrame:
    """
    Only keep rows for the pictures wanted for geo analysis
    input df: all columns from photo
    output df: owner_nsid and id of the kept photos
    """
    photos = photos[photos['accuracy'] != 0]
    return photos[['owner_nsid', 'id']]
