from pandas import read_sql_query, to_datetime
from src.core.db import get_engine
from sqlalchemy import text
from datetime import datetime

def photos():
    query = text("""--sql
            SELECT mlp.owner_nsid, mlp.id, mlp.is_test_set, mlp.reg_n_pred_date,
                    p.url_n, p.date_taken, p.date_taken_granularity,
                    p.title, p.description, p.owner_name
            FROM machine_learning_photo mlp
            JOIN photo p ON (p.owner_nsid, p.id) = (mlp.owner_nsid, mlp.id)
            WHERE mlp.sig_lip_vect_n IS NOT NULL
        """)
    df = read_sql_query(query, get_engine("server"))
    df['page_url'] = df.apply(lambda row: f"https://www.flickr.com/photos/{row['owner_nsid']}/{row['id']}", axis=1)
    df['true_date'] = to_datetime(df['date_taken'], errors='coerce').dt.year.values
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
    df = read_sql_query(query, get_engine("server"))
    df['page_url'] = df.apply(lambda row: f"https://www.flickr.com/photos/{row['owner_nsid']}/{row['id']}", axis=1)
    df['true_date'] = to_datetime(df['date_taken'], errors='coerce').dt.year.values
    df = df[df['true_date'] <= 1999]
    return df