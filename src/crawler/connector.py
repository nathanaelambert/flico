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

def get_postgresql_connection():
    # TODO: bad design: doesn't close the connection
    # TODO: should use env or something for passwords
    try:
        conn = psycopg2.connect(
            dbname="flickr_commons_metadata", 
            user="crawler", 
            password="crawler123", 
            host="localhost", 
            port="5432"
        )
    except Exception as e:
        print(f"Crawler connecting to postgresql db: {e}")

    return conn