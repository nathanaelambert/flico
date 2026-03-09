import flickrapi

from api_connector import get_flickr_endpoint

def test_institution(i=3):
    flickr = get_flickr_endpoint()
    institutions = flickr.commons.getInstitutions()['institutions']['institution']
    nsid = institutions[i]['nsid']
    name = institutions[i]['name']['_content']
    print(f"nsid: {nsid}\nname: {name}")

if __name__ == "__main__":
    test_institution()