import os
from dotenv import load_dotenv
from typing import Literal
from pgvector.psycopg2 import register_vector
from sqlalchemy import event, create_engine, text
from src.core.decorator import memoize
import pandas as pd

def get_df(user: str, columns: list[str]):
    engine = get_db_connection("server")
    query = """--sql
        SELECT mlp.owner_nsid, mlp.id, 
                mlp.is_test_set, mlp.reg_n_pred_date,
                p.url_n, p.date_taken, p.date_taken_granularity,
                p.title, p.description, p.owner_name, p.url_n
        FROM machine_learning_photo mlp
        JOIN photo p ON (p.owner_nsid, p.id) = (mlp.owner_nsid, mlp.id)
        WHERE mlp.sig_lip_vect_n IS NOT NULL
    """
    return pd.read_sql_query(query, engine)

@memoize
def get_engine(user: Literal["trainer", "crawler", "server", "dev"]):
    """Returns SQLAlchemy engine. Connect services to postgres db"""
    if user not in ["trainer", "crawler", "server", "dev"]:
        raise ValueError(f"Invalid user: {user}")
    
    load_dotenv()
    password_var = f"PWD{user.upper()}"
    password = os.getenv(password_var)

    if not password:
        raise ValueError(f"Password not found for env var: {password_var}")
    
    connection_string = (
        f"postgresql+psycopg2://{user}:{password}"
        f"@{os.getenv('PGHOST')}:{os.getenv('PGPORT', '5432')}"
        f"/{os.getenv('PGDATABASE')}"
    )
    engine = create_engine(connection_string, echo=False)
    
    @event.listens_for(engine, "connect")
    def connect(dbapi_connection, connection_record):
        register_vector(dbapi_connection, arrays=True)
    
    return engine
    
def _print_query_log(conn, cursor, statement, parameters, context, executemany):
    user = getattr(context.execution_options or {}, 'engine_user', 'unknown')
    stmt_upper = statement.strip().upper()
    if stmt_upper.startswith(('INSERT', 'UPDATE', 'DELETE')):
        action = stmt_upper.split()[0]
        rows = cursor.rowcount if hasattr(cursor, 'rowcount') else '?'
        table = next((word for word in stmt_upper.split() if '(' in word), 'unknown')
        print(f"User '{user}' {action} {rows} rows into {table}")
    else:
        print(f"User '{user}' SELECT from query")