import os
from dotenv import load_dotenv
from typing import Literal
from pgvector.psycopg2 import register_vector
import pandas as pd
from sqlalchemy import event, create_engine, text
from src.core.decorator import memoize

@memoize
def get_engine(user: Literal["trainer", "crawler", "server", "dev"]):
    """Returns SQLAlchemy engine. Connect services to postgres db"""
    if user not in ["trainer", "crawler", "server", "dev"]:
        raise ValueError(f"Invalid user: {user}")
    
    load_dotenv()
    password_var = f"PWD{user.upper()}"
    password = os.getenv(password_var)
    db = os.getenv('PGDATABASE')

    if not password:
        raise ValueError(f"Password not found for env var: {password_var}")
    if not db:
        raise ValueError(f"Database name not found. Check env var: PGDATABSE")
    
    connection_string = (
        f"postgresql+psycopg2://{user}:{password}"
        f"@{os.getenv('PGHOST')}:{os.getenv('PGPORT', '5432')}"
        f"/{db}"
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