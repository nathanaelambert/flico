import os
from dotenv import load_dotenv
from flickrapi import FlickrAPI#, FlickrError
from src.core.decorator import memoize
from src.utils.flickr import ALL_EXTRAS
# import src.utils.colors as c

@memoize
def flickr():
    load_dotenv()
    API_KEY = os.getenv('FLICKR_API_KEY')
    API_SECRET = os.getenv('FLICKR_API_SECRET')
    if not API_KEY or not API_SECRET:
        raise ValueError("FLICKR_API_KEY and FLICKR_API_SECRET must be set in .env")
    return FlickrAPI(API_KEY, API_SECRET, format='parsed-json')

def institutions():
    return flickr().commons.getInstitutions()['institutions']['institution']
    
def licenses():
    return flickr().photos.licenses.getInfo()['licenses']['license']


def pictures(owner_nsid, start_page):
    return flickr().people.getPublicPhotos(
        user_id=owner_nsid,
        per_page=500,
        page=start_page, 
        extras=ALL_EXTRAS)['photos']
