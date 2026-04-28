from sqlalchemy import text
import pandas as pd
import pandera.pandas as pa

import src.core.schema as schema

from src.core.db import get_engine
from src.utils.format import large_number_for_display

def count_flickr():
    query = text("""--sql
        WITH grouped_counts AS (
            SELECT owner_name AS institution, COUNT(*) AS downloaded
            FROM photo
            GROUP BY owner_name
        )
        SELECT institution, downloaded FROM grouped_counts
        
        UNION ALL
        
        SELECT 'TOTAL' AS institution, COUNT(*) AS downloaded FROM photo
        ORDER BY downloaded DESC
    """)
    df = pd.read_sql_query(query, get_engine("server"))
    df['downloaded'] = df['downloaded'].apply(large_number_for_display)
    return df.reset_index(drop=True)

def count_date():
    query = text("""--sql
        SELECT 'TOTAL' AS institution, COUNT(*) AS pictures FROM photo
        WHERE EXTRACT(YEAR FROM date_taken::timestamp) IS NOT NULL
        AND date_taken IS NOT NULL
        ORDER BY pictures DESC
    """)
    df = pd.read_sql_query(query, get_engine("server"))
    df['pictures'] = df['pictures'].apply(large_number_for_display)
    return df.reset_index(drop=True)

def count_description():
    query = text("""--sql
        SELECT 'TOTAL' AS institution, COUNT(*) AS pictures FROM photo
        WHERE LENGTH(description) > 0
        ORDER BY pictures DESC
    """)
    df = pd.read_sql_query(query, get_engine("server"))
    df['pictures'] = df['pictures'].apply(large_number_for_display)
    return df.reset_index(drop=True)

def sample_from_flickr():
    query = text("""--sql
        SELECT title, url_n, owner_name, date_taken, latitude, longitude
        FROM photo
        ORDER BY RANDOM()
        LIMIT 1
    """)
    df = pd.read_sql_query(query, get_engine("server"))
    return df

def unknown_date_photos():
    query = text("""--sql
            SELECT mlp.owner_nsid, mlp.id, mlp.is_test_set, mlp.reg_n_pred_date,
                    p.url_n, p.date_taken, p.date_taken_granularity,
                    p.title, p.description, p.owner_name, p.date_taken_unknown
            FROM machine_learning_photo mlp
            JOIN photo p ON (p.owner_nsid, p.id) = (mlp.owner_nsid, mlp.id)
            WHERE mlp.reg_n_pred_date IS NOT NULL AND p.date_taken_unknown is True
        """)
    df = pd.read_sql_query(query, get_engine("server"))
    df['page_url'] = df.apply(lambda row: f"https://www.flickr.com/photos/{row['owner_nsid']}/{row['id']}", axis=1)
    df['true_date'] = pd.to_datetime(df['date_taken'], errors='coerce').dt.year.values
    return df

def photos():
    query = text("""--sql
            SELECT mlp.owner_nsid, mlp.id, mlp.is_test_set, mlp.reg_n_pred_date,
                    p.url_n, p.date_taken, p.date_taken_granularity,
                    p.title, p.description, p.owner_name
            FROM machine_learning_photo mlp
            JOIN photo p ON (p.owner_nsid, p.id) = (mlp.owner_nsid, mlp.id)
            WHERE mlp.reg_n_pred_date IS NOT NULL
        """)
    df = pd.read_sql_query(query, get_engine("server"))
    df['page_url'] = df.apply(lambda row: f"https://www.flickr.com/photos/{row['owner_nsid']}/{row['id']}", axis=1)
    df['true_date'] = pd.to_datetime(df['date_taken'], errors='coerce').dt.year.values
    return df

def benchmark_photos():
    query = text("""--sql
            SELECT mlp.owner_nsid, mlp.id, mlp.is_test_set, 
                    mlp.reg_n_pred_date, mlp.qwen3_pred_date,
                    p.url_n, p.date_taken, p.date_taken_granularity,
                    p.title, p.description, p.owner_name
            FROM machine_learning_photo mlp
            JOIN photo p ON (p.owner_nsid, p.id) = (mlp.owner_nsid, mlp.id)
            WHERE mlp.reg_n_pred_date IS NOT NULL AND mlp.qwen3_pred_date IS NOT NULL
        """)
    df = pd.read_sql_query(query, get_engine("server"))
    df['page_url'] = df.apply(lambda row: f"https://www.flickr.com/photos/{row['owner_nsid']}/{row['id']}", axis=1)
    df['true_date'] = pd.to_datetime(df['date_taken'], errors='coerce').dt.year.values
    df = df[df['true_date'] <= 1999]
    return df


