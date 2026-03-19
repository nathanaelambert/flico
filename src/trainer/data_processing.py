import pandas as pd

from datetime import datetime

from ..postgresql.connector import get_db_connection

def get_dated_photos():
    """retrieves photos with dates from database"""
    engine = get_db_connection('trainer')
    query = """
    SELECT date_taken, date_taken_granularity, owner_nsid, id
    FROM photo 
    WHERE date_taken IS NOT NULL
    """
    df = pd.read_sql_query(query, engine)
    print(f"Loaded {len(df):,} photos")
    return df

def filter_dated_photos(df):
    """ only keeps photos with reasonable dates"""
    df['year'] = pd.to_datetime(df['date_taken'], errors='coerce').dt.year
    df = df.dropna(subset=['year'])
    df = df[(df['year'] >= 1850) & (df['year'] <= 2026)]
    df = df[df['owner_nsid'] != '12403504@N02'] # filtering the british library because all their dates are 2013 (unreliable dates)
    print(f"Kept   {len(df):,} photos spanning {int(df['year'].min())}–{int(df['year'].max())}")
    return df

if __name__ == "__main__":
    filter_dated_photos(get_dated_photos())

