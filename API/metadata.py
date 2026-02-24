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


def count_csv_rows(filename):
    if not filename.exists():
        return 0
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f) - 1  # -1 for header
    except:
        return 0


def get_csv_photo_ids(filename):
    if not filename.exists():
        return set()
    try:
        ids = set()
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('id'):
                    ids.add(row['id'])
        return ids
    except:
        return set()


def get_fieldnames():
    return [
        'id', 'secret', 'title', 'description', 'date_taken', 'date_uploaded',
        'latitude', 'longitude', 'comments', 'size', 'image_url', 'notes', 'tags'
    ]


def extract_from_search(photo_dict):
    if not isinstance(photo_dict, dict):
        return None
        
    def safe_extract(field):
        value = photo_dict.get(field)
        if value is None:
            return ''
        if isinstance(value, dict):
            return safe_str(value.get('_content', value))
        return safe_str(value)
    
    return {
        'id': safe_str(photo_dict.get('id')),
        'secret': safe_str(photo_dict.get('secret')),
        'title': safe_extract('title'),
        'description': safe_extract('description'),
        'date_taken': safe_str(photo_dict.get('datetaken')),
        'date_uploaded': safe_str(photo_dict.get('dateupload')),
        'latitude': safe_str(photo_dict.get('latitude')),
        'longitude': safe_str(photo_dict.get('longitude')),
        'comments': 'N/A',
        'size': f"{photo_dict.get('o_width', 'N/A')}x{photo_dict.get('o_height', 'N/A')}",
        'image_url': safe_str(photo_dict.get('url_o')),
        'notes': 'N/A',
        'tags': 'N/A'
    }


def normalize_filename(inst_name, inst_id):
    """Centralized function to generate consistent filename format."""
    # Clean institution name consistently
    cleaned_name = "".join(c for c in inst_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    return f"{cleaned_name}.csv"


# ----------------- ROUTINE 1: check local and remote ------------------- #


def check_metadata_status():
    """Routine 1: Analyze all institutions and return prioritized list."""
    print("🔍 CHECKING METADATA STATUS...")
    print("=" * 80)
    
    institutions = flickr.commons.getInstitutions()
    institution_list = institutions['institutions']['institution']
    
    status_list = []
    
    for inst in institution_list:
        inst_name = safe_str(inst.get('name', {}).get('_content', 'unknown'))
        inst_id = safe_str(inst.get('nsid'))
        csv_filename = metadata_dir / normalize_filename(inst_name, inst_id)
        
        # Get Flickr total
        flickr_total = None
        try:
            total_info = flickr.photos.search(
                user_id=inst_id, is_commons=True, per_page=1, page=1, extras='url_o'
            )
            flickr_total = int(total_info['photos'].get('total', 0))
        except Exception as e:
            print(f"❌ ERROR {inst_name}: {e}")
            continue
        
        # Get CSV count
        csv_photo_count = len(get_csv_photo_ids(csv_filename))
        csv_row_count = count_csv_rows(csv_filename) + 1  # +1 for header
        
        coverage = csv_photo_count / flickr_total if flickr_total > 0 else 1
        
        status_list.append({
            'inst': inst,
            'name': inst_name,
            'id': inst_id,
            'csv_filename': csv_filename,
            'flickr_total': flickr_total,
            'csv_photos': csv_photo_count,
            'csv_rows': csv_row_count,
            'coverage': coverage
        })
        
        print(f"{inst_name:<50} | {flickr_total:>7,} | {csv_photo_count:>7} | {coverage:>6.1%}")
    
    print("=" * 80)
    
    # Sort by ascending coverage (0% first), then by smallest total for ties
    prioritized = sorted(status_list, key=lambda x: (x['coverage'], x['flickr_total']))
    
    print(f"\n📋 PRIORITIZED LIST (lowest coverage first):")
    for i, item in enumerate(prioritized[:10], 1):  # Show top 10
        print(f"{i:2d}. {item['name']:<50} {item['coverage']:>6.1%} ({item['csv_photos']}/{item['flickr_total']:,})")
    
    return prioritized


# ----------------- ROUTINE 2: download  to local from remote ------------------- #

def download_metadata(institutions):
    """Routine 2: Download metadata for prioritized institutions."""
    fieldnames = get_fieldnames()
    
    for idx, item in enumerate(institutions, 1):
        inst = item['inst']
        inst_name = item['name']
        inst_id = item['id']
        csv_filename = item['csv_filename']
        
        flickr_total = item['flickr_total']
        
        print(f"\n[{idx}/{len(institutions)}] 🟢 DOWNLOADING {inst_name} ({inst_id})")
        print(f"  Target: {flickr_total:,} photos | CSV: {csv_filename}")
        
        # Ensure header exists if file doesn't exist or is empty
        if not csv_filename.exists() or count_csv_rows(csv_filename) == 0:
            print(f"  📝 Creating new CSV with header...")
            with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
        
        # Load existing
        existing_ids = get_csv_photo_ids(csv_filename)
        print(f"  Existing: {len(existing_ids):,} unique photos")
        
        if len(existing_ids) >= flickr_total:
            print(f"  ✅ Already complete!")
            continue
        
        page = 1
        max_pages = 10000
        new_photos_this_run = 0
        consecutive_empty_pages = 0
        empty_page_threshold = 1000
        
        while page <= max_pages and consecutive_empty_pages < empty_page_threshold:
            try:
                print(f"  📄 Page {page}...")
                photos_info = flickr.people.getPublicPhotos(
                    user_id=inst_id,
                    per_page=500,
                    page=page,
                    extras='description,date_upload,date_taken,geo,tags,o_dims,url_o,url_c,license,owner_name,views'
                )
                
                photo_batch = photos_info['photos']['photo']
                if not photo_batch:
                    print(f"  ✓ No more photos")
                    break

                print(f"  Page {page}: {len(photo_batch)} found")
                valid_new_photos = []
                new_on_page = 0
                
                for photo_dict in photo_batch:
                    photo_id = photo_dict.get('id')
                    if photo_id and photo_id not in existing_ids:
                        metadata = extract_from_search(photo_dict)
                        if metadata:
                            valid_new_photos.append(metadata)
                            existing_ids.add(photo_id)
                            new_on_page += 1
                
                print(f"  Page {page}: {new_on_page} NEW")
                consecutive_empty_pages = 0 if new_on_page > 0 else consecutive_empty_pages + 1
                
                if valid_new_photos:
                    with open(csv_filename, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writerows(valid_new_photos)
                    
                    new_photos_this_run += len(valid_new_photos)
                    print(f"  💾 Saved {len(valid_new_photos)} (run: {new_photos_this_run}, total: {len(existing_ids)})")
                else:
                    print(f"  ⚠️ No new photos (duplicates)")
                
                page += 1
                # time.sleep(random.uniform(1.5, 2.5))
                
            except flickrapi.exceptions.FlickrError as e:
                if '201:' in str(e):
                    print(f"  ⏳ Rate limited, waiting 60s...")
                    time.sleep(60)
                else:
                    print(f"  ❌ API error: {e}")
                    break
            except Exception as e:
                print(f"  ❌ Error: {e}")
                break
        
        status = "✅ COMPLETE" if len(existing_ids) >= flickr_total else "⏳ PARTIAL"
        print(f"  {status} {inst_name}: {len(existing_ids):,} photos")



# ----------------- MAIN EXECUTION ------------------- #
if __name__ == "__main__":
    print("Flickr Commons Metadata Collector")
    print("1. Check status")
    print("2. Download metadata (prioritized)")

    prioritized_institutions = check_metadata_status()
    
    response = input("\nDownload metadata now? (y/n): ").lower().strip()
    if response in ['y', 'yes']:
        print("\n🚀 STARTING DOWNLOAD (lowest coverage first)...")
        download_metadata(prioritized_institutions)
        print("\n🎉 DOWNLOAD COMPLETE!")
    else:
        print("\nℹ️ Run manually: download_metadata(prioritized_institutions)")
