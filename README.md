# flico
exploring Flickr Commons

## Dev notes
I am considering switching to the flickrapi library instead, I think it is more stable. I am getting a lot of error messages due to rate limiting.
```
201 : Sorry, the Flickr API service is not currently available.
```

## Data
Uses the Flickr Commons collection by access via its [API](https://www.flickr.com/services/api/) through Alexis Mignon's [python implementation](https://github.com/alexis-mignon/python-flickr-api)

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

## Notes for dev
Infos about how to use the API can be found [here](https://github.com/alexis-mignon/python-flickr-api/blob/master/docs/api-reference.md)
