import os
import time
import csv
import random
from pathlib import Path
from dotenv import load_dotenv
import flickrapi

# ----------------- SETUP ------------------- #
load_dotenv()
API_KEY = os.getenv('FLICKR_API_KEY')
API_SECRET = os.getenv('FLICKR_API_SECRET')
if not API_KEY or not API_SECRET:
    raise ValueError("FLICKR_API_KEY and FLICKR_API_SECRET must be set in .env")


flickr = flickrapi.FlickrAPI(API_KEY, API_SECRET, format='parsed-json')
metadata_dir = Path("metadata")
metadata_dir.mkdir(exist_ok=True)


# ----------------- UTILS ------------------- #
def safe_str(value):
    return str(value) if value is not None else ""

def print_all_institutions():
    """Print all Flickr Commons institutions with NSID and name."""
    print("🏛️  FLICKR COMMONS INSTITUTIONS")
    print("=" * 80)
    print(f"{'NSID':<20} | {'NAME':<50}")
    print("-" * 80)
    
    institutions = flickr.commons.getInstitutions()
    institution_list = institutions['institutions']['institution']
    
    for inst in institution_list:
        inst_name = safe_str(inst.get('name', {}).get('_content', 'unknown'))
        inst_id = safe_str(inst.get('nsid'))
        print(f"{inst_id:<20} | {inst_name:<50}")
    
    print("-" * 80)
    print(f"Total: {len(institution_list)} institutions")

if __name__ == "__main__":   
    print_all_institutions()
    
