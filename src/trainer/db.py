from src.core.db import get_engine
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert
import pandas as pd
import pandera.pandas as pa

class PhotoId(pa.DataFrameModel):
    owner_nsid : str
    id : int

def mark_photo(df: pa.typing.DataFrame[PhotoId]):
    """
    Mark photo creates entries in 'machine_learning_photo "
    photo table is split into two tables:
    'photo' with flickr metadata and 'machine_learning photo' with predcitions, internal params
    this separation is motivated by two things:
    1. protect flickr metadata 2. work with a lighter table (only copy useful pics)"""
    def _psql_insert_ignore(table, conn, keys, data_iter):
        # because there is no built-in pd.to_sql parameter for ON CONFLICT DO NOTHING
        data = [dict(zip(keys, row)) for row in data_iter]
        stmt = insert(table.table).values(data)
        stmt = stmt.on_conflict_do_nothing(index_elements=['owner_nsid', 'id'])
        result = conn.execute(stmt)
        return result.rowcount
    df.to_sql(
        name='machine_learning_photo',
        con=get_engine('trainer'),
        if_exists='append',
        index=False,
        method=_psql_insert_ignore,
        chunksize=1000
    )


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

