import os
from dotenv import load_dotenv

def get_db_connection():
""" responsibility of closing the connection is on caller"""
    load_dotenv()
    return = psycopg2.connect(
        dbname=os.getenv('PGDATABASE'), 
        user="server", 
        password=os.getenv('PWDSERVER'),
        host=os.getenv('PGHOST'), 
        port=os.getenv('PGPORT', '5432')
    )