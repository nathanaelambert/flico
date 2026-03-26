from src.core.db import get_engine
from sqlalchemy import text


def insert_institution(inst):
    with get_engine("crawler").connect() as conn:
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

def insert_license(license):
    with get_engine("crawler").connect() as conn:
        conn.execute(text("""--sql
            INSERT INTO license ( id,  name,  url)
            VALUES              (:id, :name, :url)
            ON CONFLICT (id) DO NOTHING
        """), [{
            "id": license['id'],
            "name": license['name'],
            "url": license['url']
        }])

def insert_picture(p):
    with get_engine('crawler').connect() as conn:
        conn.execute(text("""--sql
            INSERT INTO photo ( id,  owner_nsid,  secret,  server,  farm,  title,  is_public,  is_friend,  is_family,  license_id,  description,  original_width,  original_height,  date_upload,  last_update,  date_taken,  date_taken_granularity,  date_taken_unknown,  owner_name,   views,  tags,  machine_tags,  original_secret,  original_format,  latitude,  longitude,  accuracy,  context,  media,  media_status,  path_alias,  url_sq,  height_sq,  width_sq,  url_t,  height_t,  width_t,  url_s,  height_s,  width_s,  url_q,  height_q,  width_q,  url_m,  height_m,  width_m,  url_n,  height_n,  width_n,  url_z,  height_z,  width_z,  url_c,  height_c,  width_c,  url_l,  height_l,  width_l,  url_o,  height_o,  width_o)
            VALUES            (:id, :owner_nsid, :secret, :server, :farm, :title, :is_public, :is_friend, :is_family, :license_id, :description, :original_width, :original_height, :date_upload, :last_update, :date_taken, :date_taken_granularity, :date_taken_unknown, :owner_name,  :views, :tags, :machine_tags, :original_secret, :original_format, :latitude, :longitude, :accuracy, :context, :media, :media_status, :path_alias, :url_sq, :height_sq, :width_sq, :url_t, :height_t, :width_t, :url_s, :height_s, :width_s, :url_q, :height_q, :width_q, :url_m, :height_m, :width_m, :url_n, :height_n, :width_n, :url_z, :height_z, :width_z, :url_c, :height_c, :width_c, :url_l, :height_l, :width_l, :url_o, :height_o, :width_o)
            ON CONFLICT (id, owner_nsid) DO NOTHING
        """), [{
            'id': p['id'], 'owner_nsid': p['owner'], 'secret': p['secret'],
            'server': int(p['server']), 'farm': p['farm'], 'title': p['title'],
            'is_public': bool(p['ispublic']), 'is_friend': bool(p['isfriend']), 'is_family': bool(p['isfamily']),
            'license_id': int(p['license']), 'description': p['description']['_content'],
            'original_width': int(p['o_width']), 'original_height': int(p['o_height']),
            'date_upload': int(p['dateupload']), 'last_update': int(p['lastupdate']), 
            'date_taken': p['datetaken'], 'date_taken_granularity': int(p['datetakengranularity']),
            'date_taken_unknown': bool(p['datetakenunknown']), 'owner_name': p['ownername'],
            'views': int(p['views']), 'tags': p['tags'], 'machine_tags': p['machine_tags'],
            'original_secret': p['originalsecret'], 'original_format': p['originalformat'],
            'latitude': float(p['latitude']),'longitude': float(p['longitude']),
            'accuracy': int(p['accuracy']), 'context': int(p['context']),
            'media': p['media'], 'media_status': p['media_status'], 'path_alias': p['pathalias'],
            "url_sq": p.get("url_sq"), "height_sq": p.get("height_sq"), "width_sq": p.get("width_sq"),
            "url_t": p.get("url_t"), "height_t": p.get("height_t"), "width_t": p.get("width_t"),
            "url_s": p.get("url_s"), "height_s": p.get("height_s"), "width_s": p.get("width_s"),
            "url_q": p.get("url_q"), "height_q": p.get("height_q"), "width_q": p.get("width_q"),
            "url_m": p.get("url_m"), "height_m": p.get("height_m"), "width_m": p.get("width_m"),
            "url_n": p.get("url_n"), "height_n": p.get("height_n"), "width_n": p.get("width_n"),
            "url_z": p.get("url_z"), "height_z": p.get("height_z"), "width_z": p.get("width_z"),
            "url_c": p.get("url_c"), "height_c": p.get("height_c"), "width_c": p.get("width_c"),
            "url_l": p.get("url_l"), "height_l": p.get("height_l"), "width_l": p.get("width_l"),
            "url_o": p.get("url_o"), "height_o": p.get("height_o"), "width_o": p.get("width_o"),
        }])