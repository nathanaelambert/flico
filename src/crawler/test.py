import flickrapi

from api_connector import get_flickr_endpoint

def test_institution(i=3):
    flickr = get_flickr_endpoint()
    institutions = flickr.commons.getInstitutions()['institutions']['institution']
    nsid = institutions[i]['nsid']
    name = institutions[i]['name']['_content']
    print(f"nsid: {nsid}\nname: {name}")

def test_get_public_photos(owner_nsid="134017397@N03"):
    flickr = get_flickr_endpoint()
    photos = flickr.people.getPublicPhotos(
        user_id=owner_nsid,
        per_page=10,
        page=1,
        extras=(
            'description, license, date_upload, date_taken,'
            'owner_name, icon_server, original_format, last_update,'
            'geo, tags, machine_tags, o_dims, views, media, path_alias,'
            'url_sq, url_t, url_s, url_q, url_m, url_n, url_z, url_c, url_l, url_o'
        ),
    )['photos']
    print(f"total number of photos: {photos['total']}")
    print(photos['photo'][2])
if __name__ == "__main__":
    # test_institution()
    test_get_public_photos()