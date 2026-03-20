import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from typing import Literal
from pgvector.psycopg2 import register_vector
from sqlalchemy import event

def get_db_connection(user: Literal["trainer", "crawler", "server", "dev"]):
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
    engine = create_engine(connection_string)
    
    @event.listens_for(engine, "connect")
    def connect(dbapi_connection, connection_record):
        register_vector(dbapi_connection, arrays=True)
    
    return engine
