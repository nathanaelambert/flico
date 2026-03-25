from sqlalchemy import text
from src.core.db import get_engine

engine = get_engine("server")
with engine.connect() as conn:
    conn.execute(text("SELECT 1 AS test"))
