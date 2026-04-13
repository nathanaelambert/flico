from src.core.db import get_engine
from sqlalchemy import text
import pandas as pd

def photos_with_date_taken():
    get_query = text("""--sql
    SELECT date_taken, date_taken_granularity, owner_nsid, id
    FROM photo 
    WHERE date_taken IS NOT NULL
    """)
    return pd.read_sql_query(get_query, get_engine('trainer'))

def photos_with_description():
    get_query = text("""--sql
    SELECT date_taken, date_taken_granularity, owner_nsid, id
    FROM photo 
    WHERE description IS NOT NULL
    """)
    return pd.read_sql_query(get_query, get_engine('trainer'))

def insert_into_machine_learning_photo(df):
    """fails on attempt to insert duplicate"""
    df.to_sql(
        name='machine_learning_photo',
        con=get_engine('trainer'),
        if_exists='append',
        index=False,
        method='multi',
        chunksize=1000
    )

def photos_without_siglip_embedding():
    get_query = text("""--sql
    SELECT mlp.owner_nsid, mlp.id, p.url_n
    FROM machine_learning_photo mlp
    JOIN photo p ON (p.owner_nsid, p.id) = (mlp.owner_nsid, mlp.id)
    WHERE mlp.sig_lip_vect_n IS NULL
    """)
    photos = pd.read_sql_query(get_query, get_engine('trainer'))
    return photos

def update_siglip_embedding_picture(id: int, owner_nsid: str, embedding:list):   
    with get_engine('trainer').connect() as conn:
        result = conn.execute(text("""--sql
            UPDATE machine_learning_photo 
            SET sig_lip_vect_n = :embedding
            WHERE owner_nsid = :owner_nsid AND id = :id
        """)
        , {
            'embedding': embedding,
            'owner_nsid': owner_nsid,
            'id': id
        })
        rowcount = result.rowcount
        conn.commit()
    return rowcount > 0

def update_qwen3_pred_date(id: int, owner_nsid: str, date: int):   
    with get_engine('trainer').connect() as conn:
        result = conn.execute(text("""--sql
            UPDATE machine_learning_photo 
            SET qwen3_pred_date = :date
            WHERE owner_nsid = :owner_nsid AND id = :id
        """)
        , {
            'date': date,
            'owner_nsid': owner_nsid,
            'id': id
        })
        rowcount = result.rowcount
        conn.commit()
    return rowcount > 0

def photos_with_siglip_enbedding():
    query = """--sql
        SELECT mlp.owner_nsid, mlp.id, mlp.sig_lip_vect_n,
               mlp.is_test_set, mlp.qwen3_pred_date,
               p.url_n, p.date_taken, p.date_taken_granularity,
               p.title, p.description
        FROM machine_learning_photo mlp
        JOIN photo p ON (p.owner_nsid, p.id) = (mlp.owner_nsid, mlp.id)
        WHERE mlp.sig_lip_vect_n IS NOT NULL
    """
    photos = pd.read_sql_query(query, get_engine('trainer'))
    photos['year'] = pd.to_datetime(photos['date_taken'], errors='coerce').dt.year
    train = photos[photos["is_test_set"] == False]
    test = photos[photos["is_test_set"] == True]

    return photos, train.reset_index(drop=True), test.reset_index(drop=True)


