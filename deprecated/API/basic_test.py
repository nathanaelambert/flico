import os
from dotenv import load_dotenv
import flickr_api

"""
This simple routine makes sure that one's Flickr API key works
"""

# Load .env variables
load_dotenv()

API_KEY = os.getenv('FLICKR_API_KEY')
API_SECRET = os.getenv('FLICKR_API_SECRET')

if not API_KEY or not API_SECRET:
    raise ValueError("FLICKR_API_KEY and FLICKR_API_SECRET must be set in .env")

flickr_api.set_keys(api_key=API_KEY, api_secret=API_SECRET)

photos = flickr_api.Photo.search(tags="sunset", per_page=10)

for photo in photos:
    print(photo.title)

