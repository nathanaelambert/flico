from sqlalchemy import text
from src.crawler.flickr_api import get_flickr
from src.core.db import get_engine
    
def crawl_institutions():
    """Fetches Flickr institutions and save to PostgreSQL"""
    with get_engine("crawler").connect() as conn:
        for inst in get_flickr().commons.getInstitutions()['institutions']['institution']:
            urls = inst['urls']['url']
            conn.execute(text("""--sql
                INSERT INTO institution (nsid,  name,  date_launch,  website,  license,  flickr_page)
                VALUES                 (:nsid, :name, :date_launch, :website, :license, :flickr_page)
                ON CONFLICT (nsid) DO NOTHING
            """), [{
                "nsid": inst['nsid'],
                "name": inst['name']['_content'], 
                "date_launch": int(inst['date_launch']), 
                "website": next((url['_content'] for url in urls if url['type'] == 'site'), None), 
                "license": next((url['_content'] for url in urls if url['type'] == 'license'), None), 
                "flickr_page": next((url['_content'] for url in urls if url['type'] == 'flickr'), None)
            }])

def crawl_licenses():
    """Fetch Flickr licenses and save to PostgreSQL"""
    with get_engine("crawler").connect() as conn:
        licenses = get_flickr().photos.licenses.getInfo()['licenses']['license']
        for license in licenses:
            conn.execute(text("""--sql
                INSERT INTO license ( id,  name,  url)
                VALUES              (:id, :name, :url)
                ON CONFLICT (id) DO NOTHING
            """), [{
                "id": license['id'],
                "name": license['name'],
                "url": license['url']
            }])


if __name__ == "__main__":
    crawl_institutions()
    crawl_licenses()