import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from typing import Literal

def get_db_connection(user: Literal["trainer", "crawler", "server", "dev"]):
    """Returns SQLAlchemy engine."""
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
    return create_engine(connection_string)
