import flickrapi

from api_connector import get_flickr_endpoint


flickr = get_flickr_endpoint()

institutions = flickr.commons.getInstitutions()

example_institutions_output = """
{'institutions': 
    {
    'institution': [
        {
            'nsid': '203653061@N02', 
            'date_launch': '1760634342',
            'name': {'_content': 'Eötvös Loránd University Faculty of Law Library'}, 
            'urls': {'url': [{'type': 'site', '_content': 'https://konyvtar.ajk.elte.hu'}, {'type': 'license', '_content': 'https://www.flickr.com/people/eltelawlibrary/'}, {'type': 'flickr', '_content': 'http://flickr.com/photos/eltelawlibrary/'}]}
        }, 
        {
            'nsid': '201909310@N04',
            'date_launch': '1744906197', 
            'name': {'_content': 'Auckland War Memorial Museum Tāmaki Paenga Hira'}, 
            'urls': {'url': [{'type': 'site', '_content': 'https://www.aucklandmuseum.com/'}, {'type': 'license', '_content': 'https://www.aucklandmuseum.com/discover/collections/using-our-images'}, {'type': 'flickr', '_content': 'http://flickr.com/photos/aucklandmuseum_commons/'}]}
        }, 
        {
            'nsid': '8623220@N02', 
            'date_launch': '1200470400', 
            'name': {'_content': 'The Library of Congress'}, 
            'urls': {'url': [{'type': 'site', '_content': 'http://www.loc.gov/'}, {'type': 'license', '_content': 'http://www.loc.gov/rr/print/195_copr.html#noknown'}, {'type': 'flickr', '_content': 'http://flickr.com/photos/library_of_congress/'}]}
        }
    ]
    },
    'stat': 'ok'
}

print(institutions)

# photos = flickr.people.getPublicPhotos(
#     user_id=inst_id,
#     per_page=500,
#     page=page,
#     extras=(
#         'description, license, date_upload, date_taken,'
#         'owner_name, icon_server, original_format, last_update,'
#         'geo, tags, machine_tags, o_dims, views, media, path_alias,'
#         'url_sq, url_t, url_s, url_q, url_m, url_n, url_z, url_c, url_l, url_o'
#     ),
# )
example_photos = """
<photos page="2" pages="89" perpage="10" total="881">
	<photo id="2636" owner="47058503995@N01" 
		secret="a123456" server="2" title="test_04"
		ispublic="1" isfriend="0" isfamily="0" />
	<photo id="2635" owner="47058503995@N01"
		secret="b123456" server="2" title="test_03"
		ispublic="0" isfriend="1" isfamily="1" />
	<photo id="2633" owner="47058503995@N01"
		secret="c123456" server="2" title="test_01"
		ispublic="1" isfriend="0" isfamily="0" />
	<photo id="2610" owner="12037949754@N01"
		secret="d123456" server="2" title="00_tall"
		ispublic="1" isfriend="0" isfamily="0" />
</photos>
"""


"""
USER.GET_PUBLIC_PHOTOS
1: Required arguments missing
2: Unknown user
    A user_id was passed which did not match a valid flickr user.
5: User deleted
    The user id passed did not match a Flickr user.
100: Invalid API Key
    The API key passed was not valid or has expired.
105: Service currently unavailable
    The requested service is temporarily unavailable.
106: Write operation failed
    The requested operation failed due to a temporary issue.
111: Format "xxx" not found
    The requested response format was not found.
112: Method "xxx" not found
    The requested method was not found.
114: Invalid SOAP envelope
    The SOAP envelope send in the request could not be parsed.
115: Invalid XML-RPC Method Call
    The XML-RPC request document could not be parsed.
116: Bad URL found
    One or more arguments contained a URL that has been used for abuse on Flickr. 
"""