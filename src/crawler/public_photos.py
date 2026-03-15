import os
import flickrapi
import psycopg2

from dotenv import load_dotenv

from connector import get_flickr_endpoint

RESET = '\033[0m'
WHITE = '\033[97m'
GREY =  '\033[90m' 
RED =  '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
CYAN = '\033[36m'  


def get_public_photos(owner_nsid: str, owner_name: str):
    """Fetch Flickr photos from institution and save to PostgreSQL"""
    flickr = get_flickr_endpoint()
    load_dotenv()
    conn = psycopg2.connect(dbname=os.getenv('PGDATABASE'), 
        user="crawler", password=os.getenv('PWDCRAWLER'),
        host=os.getenv('PGHOST'), port=os.getenv('PGPORT', '5432')
    )
    start_page = 1
    while start_page > 0:
        total, page, perpage, pages, errors, duplicates = _run_a_batch(owner_nsid, 
                                                           conn, flickr, start_page)
        pics_saved = perpage - len(errors) - duplicates
        match pics_saved:
            case 500:
                color_pics = GREEN
            case 0:
                color_pics = GREY
            case _:
                color_pics = YELLOW
        print(f"{GREY}page {RESET}"
              f"{WHITE}{page:03d}{RESET}"
              f"{GREY} / {pages:03d} :{RESET} "
              f"{color_pics}{pics_saved:03d}{RESET}"
              f"{GREY} pics downloaded from {WHITE}{owner_name}{RESET}"
              f"{GREY}, {owner_nsid}{RESET}")
        if page < pages:
            start_page += 1
        else:
            start_page = 0 
    conn.close()

def _run_a_batch(owner_nsid, connection, flickr, start_page=1):
    duplicates = 0
    errors = []
    cur = connection.cursor()
    try:
        photos = flickr.people.getPublicPhotos(user_id=owner_nsid,
            per_page=500, page=start_page, extras=('description, license, date_upload,' 
                'date_taken, owner_name, icon_server, original_format, last_update,geo,'
                'tags, machine_tags, o_dims, views, media, path_alias, url_sq, url_t,'
                'url_s, url_q, url_m, url_n, url_z, url_c, url_l, url_o'),
        )['photos']
    except flickrapi.exceptions.FlickrError as e:
        print(f"{RED}Flickr API error page {start_page}: {e}{RESET}")
        return 0, start_page, 0, 0, errors, duplicates
    for p in photos['photo']:
        try:
            cur.execute(_photo_insert_query(), {
                'id': p['id'], 'owner': p['owner'], 'secret': p['secret'],
                'server': int(p['server']), 'farm': p['farm'], 'title': p['title'],
                'ispublic': bool(p['ispublic']), 'isfriend': bool(p['isfriend']), 'isfamily': bool(p['isfamily']),
                'license': int(p['license']), 'description': p['description']['_content'],
                'o_width': int(p['o_width']), 'o_height': int(p['o_height']),
                'dateupload': int(p['dateupload']), 'lastupdate': int(p['lastupdate']), 
                'datetaken': p['datetaken'], 'datetakengranularity': int(p['datetakengranularity']),
                'datetakenunknown': bool(p['datetakenunknown']), 'ownername': p['ownername'],
                'views': int(p['views']), 'tags': p['tags'], 'machine_tags': p['machine_tags'],
                'originalsecret': p['originalsecret'], 'originalformat': p['originalformat'],
                'latitude': float(p['latitude']),'longitude': float(p['longitude']),
                'accuracy': int(p['accuracy']), 'context': int(p['context']),
                'media': p['media'], 'media_status': p['media_status'], 'pathalias': p['pathalias'],
                "url_sq":          p.get("url_sq"),
                "height_sq":       p.get("height_sq"),
                "width_sq":        p.get("width_sq"),
                "url_t":           p.get("url_t"),
                "height_t":        p.get("height_t"),
                "width_t":         p.get("width_t"),
                "url_s":           p.get("url_s"),
                "height_s":        p.get("height_s"),
                "width_s":         p.get("width_s"),
                "url_q":           p.get("url_q"),
                "height_q":        p.get("height_q"),
                "width_q":         p.get("width_q"),
                "url_m":           p.get("url_m"),
                "height_m":        p.get("height_m"),
                "width_m":         p.get("width_m"),
                "url_n":           p.get("url_n"),
                "height_n":        p.get("height_n"),
                "width_n":         p.get("width_n"),
                "url_z":           p.get("url_z"),
                "height_z":        p.get("height_z"),
                "width_z":         p.get("width_z"),
                "url_c":           p.get("url_c"),
                "height_c":        p.get("height_c"),
                "width_c":         p.get("width_c"),
                "url_l":           p.get("url_l"),
                "height_l":        p.get("height_l"),
                "width_l":         p.get("width_l"),
                "url_o":           p.get("url_o"),
                "height_o":        p.get("height_o"),
                "width_o":         p.get("width_o"),
            })
            if not cur.fetchone():
                duplicates += 1
        except psycopg2.Error as e:
            print(f"{RED}Photo {p['id']}: {e}{RESET}")
            errors.append(f"Photo {p['id']}: {e}")
    connection.commit()
    cur.close()
    return photos['total'], photos['page'], photos['perpage'], photos['pages'], errors, duplicates
    

def _photo_insert_query():
    return """
        INSERT INTO photo (
            id, owner_nsid, secret,
            server, farm, title,
            is_public, is_friend, is_family,
            license_id, description,
            original_width, original_height,
            date_upload, last_update, 
            date_taken, date_taken_granularity, 
            date_taken_unknown, owner_name,
            views, tags, machine_tags,
            original_secret, original_format,
            latitude, longitude, 
            accuracy, context,
            media, media_status, path_alias,
            url_sq, height_sq, width_sq,
            url_t, height_t, width_t,
            url_s, height_s, width_s,
            url_q, height_q, width_q,
            url_m, height_m, width_m,
            url_n, height_n, width_n,
            url_z, height_z, width_z,
            url_c, height_c, width_c,
            url_l, height_l, width_l,
            url_o, height_o, width_o
        )
        VALUES (
            %(id)s, %(owner)s, %(secret)s,
            %(server)s, %(farm)s, %(title)s,
            %(ispublic)s, %(isfriend)s, %(isfamily)s,
            %(license)s, %(description)s,
            %(o_width)s, %(o_height)s,
            %(dateupload)s, %(lastupdate)s,
            %(datetaken)s, %(datetakengranularity)s,
            %(datetakenunknown)s, %(ownername)s,
            %(views)s, %(tags)s, %(machine_tags)s,
            %(originalsecret)s, %(originalformat)s,
            %(latitude)s, %(longitude)s, 
            %(accuracy)s, %(context)s,
            %(media)s, %(media_status)s, %(pathalias)s,
            %(url_sq)s, %(height_sq)s, %(width_sq)s,
            %(url_t)s, %(height_t)s, %(width_t)s,
            %(url_s)s, %(height_s)s, %(width_s)s,
            %(url_q)s, %(height_q)s, %(width_q)s,
            %(url_m)s, %(height_m)s, %(width_m)s,
            %(url_n)s, %(height_n)s, %(width_n)s,
            %(url_z)s, %(height_z)s, %(width_z)s,
            %(url_c)s, %(height_c)s, %(width_c)s,
            %(url_l)s, %(height_l)s, %(width_l)s,
            %(url_o)s, %(height_o)s, %(width_o)s
        )
        ON CONFLICT (owner_nsid, id) DO NOTHING
        RETURNING id;
        """

if __name__ == "__main__":
    get_public_photos(owner_nsid="8623220@N02", owner_name="Library of Congress") #the library of congress
