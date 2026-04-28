from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert, array
from sqlalchemy.sql import table, column, bindparam
from sqlalchemy import update, func
from sqlalchemy.orm import sessionmaker
import pandas as pd
from typing import Callable
import pandera.pandas as pa
from pandera.typing import DataFrame
from sklearn.model_selection import train_test_split
from src.core.db import get_engine
import src.core.schema as schema
from src.core.decorator import memoize
from src.core.models import MachineLearningPhoto


@memoize
def flickr_photo() -> pa.typing.DataFrame[schema.Photo]:
    query = text("""--sql
        SELECT * FROM photo
        LIMIT 100 --TODO remove this line later
    """)
    df = pd.read_sql_query(query, get_engine("server"))
    return schema.Photo.validate(df) 

def _mark_photo(df: DataFrame[schema.PhotoId]):
    """
    creates entries in machine_learning_photo 
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
    df[['owner_nsid', 'id']].to_sql(
        name='machine_learning_photo',
        con=get_engine('trainer'),
        if_exists='append',
        index=False,
        method=_psql_insert_ignore,
        chunksize=1000
    )

def use_for_geo(df: DataFrame[schema.PhotoId]):
    _mark_photo(df)
    # TODO 
    # Mark flags in db: (sql update)
    # geo_valid_set = True
    pass

def use_for_date(df: DataFrame[schema.PhotoId]) -> None:
    """Split data and bulk update train/test flags."""
    _mark_photo(df)
    df_train, df_test = train_test_split(df, test_size=0.2, random_state=42)
    df_train = df_train.assign(is_date_train=True, is_date_test=False)
    df_test = df_test.assign(is_date_train=False, is_date_test=True)
    df_merged = pd.concat([df_train, df_test]).sort_index()
    create_ml_photo_updater('is_date_train')(df_merged)
    create_ml_photo_updater('is_date_test')(df_merged)

def create_ml_photo_updater(column_name: str) -> Callable[[pd.DataFrame], None]:
    """Creates column updater with schema validation + bulk insert."""
    if column_name not in schema.MLPhoto.to_schema().columns:
        raise ValueError(f"Unknown column: {column_name}")
    col = schema.MLPhoto.to_schema().columns[column_name]
    field_schema = schema.MLPhoto.to_schema().columns[column_name]
    def ml_photo_updater(df: pd.DataFrame) -> None:
        required_cols = ['owner_nsid', 'id', column_name]
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise ValueError(f"Missing columns: {missing}")
        series_schema = pa.SeriesSchema(
            dtype=col.dtype,
            nullable=getattr(col, 'nullable', False),
            coerce=getattr(col, 'coerce', False),
            checks=getattr(col, 'checks', []),
        )
        validated_values = series_schema.validate(df[column_name])
        update_df = df[required_cols[:-1]].copy()  # owner_nsid, id
        update_df['value'] = validated_values

        affected = 0
        for _, row in update_df.iterrows():
            with get_engine('trainer').connect() as conn:
                result = conn.execute(text(f"""--sql
                    UPDATE machine_learning_photo 
                    SET {column_name} = :value
                    WHERE owner_nsid = :owner_nsid AND id = :id
                """)
                , {
                    'value': row['value'],
                    'owner_nsid': row['owner_nsid'],
                    'id': row['id']
                })
                affected += result.rowcount
                conn.commit()
        print(f"Wrote data in column {column_name}. {affected} rows affected")
    return ml_photo_updater
    
def rm_data_ml_photo(column_name: str) -> None:
    if column_name not in schema.MLPhoto.to_schema().columns:
        raise ValueError(f"Unknown column: {column_name}")
    affected = 0
    with get_engine('trainer').connect() as conn:
        result = conn.execute(text(f"""--sql
            UPDATE machine_learning_photo 
            SET {column_name} = NULL
            WHERE {column_name} is not NULL
        """))
        affected += result.rowcount
        conn.commit()
    print(f"Removed data in column {column_name}. {affected} rows affected")
        
    

