# flico
exploring Flickr Commons

## Data
Uses the Flickr Commons collection by access via its [API](https://www.flickr.com/services/api/) 

through Alexis Mignon's [python implementation](https://github.com/alexis-mignon/python-flickr-api), ([docs](https://github.com/alexis-mignon/python-flickr-api/blob/master/docs/api-reference.md)
)

and/or

through the python library [flickrapi](https://pypi.org/project/flickrapi/)

## Setup for devs
1. clone repo 
```
git clone git@github.com:nathanaelambert/flico.git
```
2. copy and rename `.env.example` as `.env`
3. put your Flickr API key and secret in the `.env` file
4. create a python virtual environment
```
python -m venv .venv
```
5. Activate the venv
```
source .venv/bin/activate
```
6. install pip requirements
```
python -m pip install pip-requirements.txt
```
7. check that API key works
```
python API/basic_test.py
```


# Dev notes

## Feb 23 2026
I am considering switching to the flickrapi library instead, I think it is more stable.


I am getting a lot of error messages due to rate limiting.
```
201 : Sorry, the Flickr API service is not currently available.
```

Flickr limits the access to the API per key. They ask for us to stay under **3600 queries per hour** across the whole key (which means the aggregate of all the users of the integration).

Trying to use `extras` in search instead of `photo.getInfo`. (With one `search` query I can get 500 photos, while `getInfo`must be called on **every** photo).

Not all metadata can be obtained with `extras`
```    Skipping malformed photo: 'str' object has no attribute 'get'
extras="description,license,date_upload,date_taken,owner_name,geo,tags,machine_tags,o_dims,views,url_o,url_c"
```


| Field         | Available via extras? | Notes                                                            |
| ------------- | --------------------- | ---------------------------------------------------------------- |
| id            | ✅ Yes                 | Always in search results                                         |
| secret        | ✅ Yes                 | Always included                                                  |
| title         | ❌ No*                 | *Basic title sometimes in search, but full title needs getInfo() |
| description   | ✅ Yes                 | photo.description._content                                       |
| date_taken    | ✅ Yes                 | photo.datetaken                                                  |
| date_uploaded | ✅ Yes                 | photo.dateupload (Unix timestamp)                                |
| locations     | ✅ Yes                 | photo.latitude, photo.longitude                                  |
| comments      | ❌ No                  | Needs getInfo()                                                  |
| size          | ✅ Yes                 | url_o + o_width/o_height from o_dims                             |
| image_url     | ✅ Yes                 | url_o, url_c, url_m, etc.                                        |
| notes         | ❌ No                  | Needs getInfo()                                                  |
| tags          | ✅ Yes                 | photo.tags.tag[] array                                           |