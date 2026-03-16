import os
from dotenv import load_dotenv
import flickrapi
import psycopg2


def get_flickr_endpoint():
    load_dotenv()
    API_KEY = os.getenv('FLICKR_API_KEY')
    API_SECRET = os.getenv('FLICKR_API_SECRET')
    if not API_KEY or not API_SECRET:
        raise ValueError("FLICKR_API_KEY and FLICKR_API_SECRET must be set in .env")
    return flickrapi.FlickrAPI(API_KEY, API_SECRET, format='parsed-json')

def get_db_connection():
    """ responsibility of closing the connection is on caller"""
    load_dotenv()
    return = psycopg2.connect(
        dbname=os.getenv('PGDATABASE'), 
        user="crawler", 
        password=os.getenv('PWDCRAWLER'),
        host=os.getenv('PGHOST'), 
        port=os.getenv('PGPORT', '5432')
    )