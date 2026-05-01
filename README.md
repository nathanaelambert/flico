# flico
exploring Flickr Commons

## Data
Uses the Flickr Commons collection by access via its [API](https://www.flickr.com/services/api/) 

through the python library [flickrapi](https://pypi.org/project/flickrapi/)

## Setup for devs
- clone repo 
```
git clone git@github.com:nathanaelambert/flico.git
```
- copy and rename [.env.example](.env.example) as `.env`
- put your Flickr API key and secret in the `.env` file
- put the correct database host and port in `.env`
- put the correct password for your database user (dev) in `.env`
- create a python virtual environment
```
python -m venv .venv
```
- activate the venv
```
source .venv/bin/activate
```
- from root folder : install python package in dev mode
```
pip install -e .
```

## Instructions for Dev
The 3 services and their responsibility:
1. src.crawler.db
keeping the photo table updated with flickr pics 
2. src.server.db
giving info about the data in the db, for monitoring and visuals
3. src.trainer.db 
reading and writing the processed data of the main pipelines

If you need to read or write something, look in the coresponding module for existing methods to call. If non exist, write one.

## TUTORIAL how to alter remote db schema
- connect to EPFL vpn
- connect as app
```
psql -h flickr-dev.postgresql.dbaas.intranet.epfl.ch -p 5432 -U app -d app
```
- enter password
2. alter schema
```--sql
ALTER TABLE machine_learning_photo
ADD column_name datatype;
```

## TUTORIAL how to copy from local db to remote db (after schema is updated)


# Dev logs
## May 1 2026
database read and write seems to work
## April 29 2026
I'm trying to fix the sqlalchemy interface with the db
It's very annoying because types don't match between dataframes
and the sql db
## April 13 2026

Qwen predictions are done and evaluated. Image processing yields 11 years mae, while QWEN3 yields 16 years of mae (both on test set).

Trainer image pipeline might still be broken.

starting to work on textual data: extracting date from description.


## April 1 2026
Estimated cost and duration for Qwen3 preds: 33h 8chf


connection to remote db
```
psql -h flickr-dev.postgresql.dbaas.intranet.epfl.ch -p 5432 -U dev -d app
```

hôte : flickr-dev.postgresql.dbaas.intranet.epfl.ch port : 5432 base : app

## March 31 2026
Completed the irst pipeline from Flickr -> predicted date.
Observed issues with post 2000 dates. 
Considering comparing perfs with commercial MLLM before 2000. 
Using QWen3 vision.
Working code, but slow (10s per pic).
Need async to fire more queries I guess.
Run in pgadmin to monitor progress:
```--sql
SELECT id, owner_nsid, qwen3_pred_date FROM public.machine_learning_photo
WHERE qwen3_pred_date is NOT NULL
```
## March 26 2026
Refactored the crawler
For now the trainer is a broken mess
Frustrated with plotly because the interactivity doesn't scale well in my opinion
going to try bokeh

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
sudo -i -u postgres 
psql -f flickr_commons_metadata.sql
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
