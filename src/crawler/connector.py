import os
from dotenv import load_dotenv
import flickrapi


def get_flickr_endpoint():
    load_dotenv()
    API_KEY = os.getenv('FLICKR_API_KEY')
    API_SECRET = os.getenv('FLICKR_API_SECRET')
    if not API_KEY or not API_SECRET:
        raise ValueError("FLICKR_API_KEY and FLICKR_API_SECRET must be set in .env")
    return flickrapi.FlickrAPI(API_KEY, API_SECRET, format='parsed-json')
