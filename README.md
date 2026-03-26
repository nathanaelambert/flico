# flico
exploring Flickr Commons

## Data
Uses the Flickr Commons collection by access via its [API](https://www.flickr.com/services/api/) 

through the python library [flickrapi](https://pypi.org/project/flickrapi/)

## Setup for devs
1. clone repo 
```
git clone git@github.com:nathanaelambert/flico.git
```
2. copy and rename [.env.example](.env.example) as `.env`
3. put your Flickr API key and secret in the `.env` file
4. put the correct database host and port in `.env`
5. put the correct password for your database user (dev) in `.env`
6. create a python virtual environment
```
python -m venv .venv
```
7. Activate the venv
```
source .venv/bin/activate
```
8. install pip requirements
```
python -m pip install pip-requirements.txt
```
9. run the [basic test](API/basic_test.py) to check that the API works
```
python API/basic_test.py
```


# Dev logs
## March 25 2026
Some good decent predictions with SVR 
reformatting project structure due to weird imports
TODO: refactor trainer
TODO: refactor public.photos


## March 19 2026
Installing pgvector 
```
sudo apt install postgresql-18-pgvector
```
## March 13 2026
Current method consisted in copy/paste sql as superuser for db creation.
Connecting via psycopg2 as crawler to download institutions

installing (with snap) `pgadmin4` because I'm sick of the ugly CLI
## March 12 2026
1. Installing postgres locally (on ubuntu)
```
sudo apt install postgresql
```
2. Starting the daemon on TCP 5432 with systemctl
```
sudo systemctl status postgresql     # Check if PostgreSQL is running
sudo systemctl start postgresql      # Start PostgreSQL  
sudo systemctl enable postgresql     # Auto-start on boot
```
3. connecting as interactive postgres user (changes shell context) and executing script
```
sudo -i -u postgres psql -f flickr_commons_metadata.sql
```

Other useful commands
```
sudo systemctl stop postgresql       # Stop PostgreSQL daemon
sudo systemctl restart postgresql    # Restart PostgreSQL
```

## march 9 2026
need migration manager and version control?
Using postgresql database

## March 3 2026
Focusing on time aspect. Will incorporate image analysis in pipeline. Probably reverse image search.

## Feb 24 2026

Had to fixed a **truncating issue**:
Flickr behaviors for high-volume Commons accounts: search scopes or server-side caps truncate results without error.
FIX:
Replaced `flickr.photos.search(user_id=inst_id, is_commons=True, ...)` with `flickr.people.getPublicPhotos(user_id=inst_id, ...)`.

[metadata script](API/metadata.py) script seems ok.

I checked the [Royal Museums Greenwhich](https://www.flickr.com/photos/nationalmaritimemuseum/with/38608148550/) that has 0 photos obtainable via search with the API. It seems that their pictures are copyrighted so it makes sense. This means that copyrighted picture don't appear.

## Feb 23 2026

| Field         | Available via extras? | Notes                                                            |
| ------------- | --------------------- | ---------------------------------------------------------------- |
| id            | ✅ Yes                 | Always in search results                                         |
| secret        | ✅ Yes                 | Always included                                                  |
| title         | ❌ No* (good enough)   | *Basic title sometimes in search, but full title needs getInfo() |
| description   | ✅ Yes                 | photo.description._content                                       |
| date_taken    | ✅ Yes                 | photo.datetaken                                                  |
| date_uploaded | ✅ Yes                 | photo.dateupload (Unix timestamp)                                |
| locations     | ✅ Yes                 | photo.latitude, photo.longitude                                  |
| comments      | ❌ No                  | Needs getInfo()                                                  |
| size          | ✅ Yes                 | url_o + o_width/o_height from o_dims                             |
| image_url     | ✅ Yes                 | url_o, url_c, url_m, etc.                                        |
| notes         | ❌ No                  | Needs getInfo()                                                  |
| tags          | ✅ Yes                 | photo.tags.tag[] array                                           |


Not all metadata can be obtained with `extras`
```    Skipping malformed photo: 'str' object has no attribute 'get'
extras="description,license,date_upload,date_taken,owner_name,geo,tags,machine_tags,o_dims,views,url_o,url_c"
```

Trying to use `extras` in search instead of `photo.getInfo`. (With one `search` query I can get 500 photos, while `getInfo`must be called on **every** photo).

Flickr limits the access to the API per key. They ask for us to stay under **3600 queries per hour** across the whole key (which means the aggregate of all the users of the integration).

I am getting a lot of error messages due to rate limiting.
```
201 : Sorry, the Flickr API service is not currently available.
```

I am switching to the flickrapi library instead, I think it is more stable.
