import os
import flickrapi
import psycopg2

from dotenv import load_dotenv

from connector import get_flickr_endpoint
    
def crawl_institutions():
    """Fetch Flickr institutions and save to PostgreSQL"""
    flickr = get_flickr_endpoint()
    load_dotenv()
    conn = psycopg2.connect(
        dbname=os.getenv('PGDATABASE'), 
        user="crawler", 
        password=os.getenv('PWDCRAWLER'),
        host=os.getenv('PGHOST'), 
        port=os.getenv('PGPORT', '5432')
    )
    
    cur = conn.cursor()
    try:
        for inst in flickr.commons.getInstitutions()['institutions']['institution']:
            nsid = inst['nsid']
            name = inst['name']['_content']
            date_launch = int(inst['date_launch'])
            urls = inst['urls']['url']
            website = next((url['_content'] for url in urls if url['type'] == 'site'), None)
            license_url = next((url['_content'] for url in urls if url['type'] == 'license'), None)
            flickr_page = next((url['_content'] for url in urls if url['type'] == 'flickr'), None)
            
            cur.execute("""
                INSERT INTO institution (nsid, name, date_launch, website, license, flickr_page)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (nsid) DO NOTHING  -- Skip duplicates
            """, (nsid, name, date_launch, website, license_url, flickr_page))
        conn.commit()

    except Exception as e:
        print(e)
        conn.rollback()

    finally:
        cur.close()
        conn.close()

def crawl_licenses():
    """Fetch Flickr licenses and save to PostgreSQL"""
    flickr = get_flickr_endpoint()
    load_dotenv()
    conn = psycopg2.connect(
        dbname=os.getenv('PGDATABASE'), 
        user="crawler", 
        password=os.getenv('PWDCRAWLER'),
        host=os.getenv('PGHOST'), 
        port=os.getenv('PGPORT', '5432')
    )
    
    cur = conn.cursor()
    licenses = flickr.photos.licenses.getInfo()['licenses']['license']
    try:
        for license in licenses:
            id = license['id']
            name = license['name']
            url = license['url']

            cur.execute("""
                INSERT INTO license (id, name, url)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO NOTHING  -- Skip duplicates
            """, (id, name, url))
        conn.commit()

    except Exception as e:
        print(f"Flickr API: {e}")
        conn.rollback()

    finally:
        cur.close()
        conn.close()

def test_psycop():
    load_dotenv()
    conn = psycopg2.connect(
        dbname=os.getenv('PGDATABASE'), 
        user="crawler", 
        password=os.getenv('PWDCRAWLER'),
        host=os.getenv('PGHOST'), 
        port=os.getenv('PGPORT', '5432')
    )
    cur = conn.cursor()
    cur.execute("SELECT 1 AS test;")
    result = cur.fetchone() 
    print(result) 
    cur.close()
    conn.close()

if __name__ == "__main__":
    crawl_institutions()
    crawl_licenses()
    # test_psycop()