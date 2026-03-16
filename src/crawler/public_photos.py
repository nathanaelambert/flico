import os
import flickrapi
import psycopg2

from dotenv import load_dotenv

from connector import get_flickr_endpoint, get_db_connection

RESET = '\033[0m'
WHITE = '\033[97m'
GREY =  '\033[90m' 
RED =  '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
BLUE = '\033[34m'
CYAN = '\033[36m'  

def get_public_photos(owner_nsid: str, conn, flickr, owner_name: str):
    """Fetch Flickr photos from institution and save to PostgreSQL"""
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
    institutions = [
        ### COMPLETED (march 16 2026)
        # ("8623220@N02",	"The Library of Congress"),
        # ("100017484@N04",	"LetterformArchive"),
        # ("104959762@N04",	"Cloyne & District Historical Society"),
        # ("105662205@N04",	"UC Berkeley, Department of Geography"),
        # ("107895189@N03",	"Tasmanian Archives and State Library (Commons)"),
        # ("108605878@N06",	"The Finnish Museum of Photography"),
        # ("108745105@N04",	"UBC Library Digitization Centre"),
        # ("109550159@N08",	"Costică Acsinte Archive"),

        ### TO DOWNLOAD
        ("123233489@N03",	"Aalto University Library and Archive Commons"),
        ("12403504@N02",	"The British Library"),
        ("124327652@N02",	"tyrrellhistoricallibrary"),
        ("124344537@N02",	"The Graduate Institute, Geneva"),
        ("124448282@N08",	"Huron County Museum & Historic Gaol"),
        ("124495553@N05",	"Archives of the Finnish Broadcasting Company Yle"),
        ("125149169@N06",	"Vestfoldmuseene | Vestfold Museums"),
        ("126364681@N08",	"Congregation of Sisters of St. Joseph in Canada"),
        ("126377022@N07",	"Internet Archive Book Images"),
        ("126398744@N08",	"The Gallen-Kallela Museum"),
        ("126472954@N08",	"Université de Caen Normandie"),
        ("127336509@N06",	"Senado Federal do Brasil"),
        ("128445772@N04",	"Presidency Of The Republic Of Turkey Directorate o"),
        ("128520551@N04",	"UVicLibraries"),
        ("130536320@N07",	"VCU Libraries Commons"),
        ("133323184@N07",	"Camden Public Library (Maine)"),
        ("134017397@N03",	"Community Archives of Belleville & Hastings County"),
        ("134319968@N02",	"Colección Amadeo León - Boconó"),
        ("135637350@N04",	"American Aviation Historical Society"),
        ("138361426@N08",	"East Riding Archives"),
        ("142575440@N02",	"Liberas"),
        ("14456531@N07",	"National Library of Scotland"),
        ("145517650@N04",	"Armenian Studies Program, Fresno State"),
        ("148865600@N02",	"Halifax Municipal Archives"),
        ("150408343@N02",	"Médiathèques Valence Romans agglomération"),
        ("164711667@N06",	"CADL_LocalHistory"),
        ("201312638@N04",	"Randolph Historical VT"),
        ("201555210@N04",	"archivesatncbs"),
        ("201585368@N05",	"Boston Public Library Digital"),
        ("201627032@N02",	"Marshall Public Library"),
        ("201909310@N04",	"Auckland War Memorial Museum Tāmaki Paenga Hira"),
        ("203653061@N02",	"Eötvös Loránd University Faculty of Law Library"),
        ("23121382@N07",	"Deseronto Archives"),
        ("23686862@N03",	"Galt Museum & Archives on The Commons"),
        ("24785917@N03",	"Powerhouse Museum Collection"),
        ("25053835@N03",	"Smithsonian Institution"),
        ("25786829@N08",	"Musée McCord Stewart Museum"),
        ("25960495@N06",	"Keene and Cheshire County (NH) Historical Photos"),
        ("26134435@N05",	"bibliothequedetoulouse"),
        ("26491575@N05",	"Library Company of Philadelphia"),
        ("26808453@N03",	"National Science and Media Museum"),
        ("27331537@N06",	"MHNSW - State Archives Collection"),
        ("29295370@N07",	"North East Museums"),
        ("29454428@N08",	"State Library of NSW"),
        ("29998366@N02",	"Nationaal Archief"),
        ("30115723@N02",	"Australian War Memorial collection"),
        ("30194653@N06",	"The Library of Virginia"),
        ("30515687@N05",	"Cornell University Library"),
        ("30835311@N07",	"National Galleries of Scotland Commons"),
        ("31033598@N03",	"Miami U. Libraries - Digital Collections"),
        ("31575009@N05",	"The National Archives UK"),
        ("31846825@N04",	"State Library and Archives of Florida"),
        ("32300107@N06",	"IWM Collections"),
        ("32605636@N06",	"State Library of Queensland, Australia"),
        ("32741315@N06",	"National Library NZ on The Commons"),
        ("32951986@N05",	"New York Public Library"),
        ("33147718@N05",	"Australian National Maritime Museum on The Commons"),
        ("34101160@N07",	"nha.library"),
        ("34419668@N08",	"Swedish National Heritage Board"),
        ("34586311@N05",	"OSU Special Collections & Archives : Commons"),
        ("35128489@N07",	"LSE Library"),
        ("35310696@N04",	"The Field Museum Library"),
        ("35532303@N08",	"Getty Research Institute"),
        ("35740357@N03",	"U.S. National Archives"),
        ("35978124@N04",	"Faculty of Music, Trinity Laban"),
        ("36038586@N04",	"DC Public Library Commons"),
        ("36281769@N04",	"JWA Commons"),
        ("36988361@N08",	"Center for Jewish History, NYC"),
        ("37199428@N06",	"LlGC ~ NLW"),
        ("37381115@N04",	"Bergen Public Library"),
        ("37547255@N08",	"Fylkesarkivet i Vestland"),
        ("37784107@N08",	"UA Archives | Upper Arlington History"),
        ("37979087@N05",	"San Francisco Public Library"),
        ("38561291@N04",	"Archives of the Law Society of Ontario"),
        ("39758725@N03",	"Dundas Museum and Archives"),
        ("41131493@N06",	"SMU Libraries Digital Collections"),
        ("41815917@N06",	"Woodrow Wilson Presidential Library Archives"),
        ("44494372@N05",	"NASA on The Commons"),
        ("45270502@N06",	"Royal Danish Library"),
        ("47154409@N06",	"Het Nieuwe Instituut - Architecture Collection"),
        ("47290943@N03",	"National Library of Ireland on The Commons"),
        ("47326604@N02",	"Texas State Archives"),
        ("47756470@N03",	"Archives of Medicine - NLM - NIH"),
        ("47908901@N03",	"Museum of Hartlepool"),
        ("48220291@N04",	"National Library of Norway"),
        ("48641766@N05",	"Svenska litteratursällskapet i Finland"),
        ("52529054@N06",	"Mennonite Church USA Archives"),
        ("54403180@N04",	"Public Record Office of Northern Ireland"),
        ("56434318@N05",	"Preus museum"),
        ("59811348@N05",	"Nasjonalarkivet (The National Archives of Norway)"),
        ("60147353@N07",	"Salt Research"),
        ("61270229@N05",	"NavyMedicine"),
        ("61498590@N03",	"Museum of Photographic Arts Collections"),
        ("62173425@N02",	"Stockholm Transport Museum Commons"),
        ("67193564@N03",	"National Library of Australia Commons"),
        ("69269002@N04",	"libraryrahs@gmail.com"),
        ("7167652@N06",	"George Eastman Museum"),
        ("8337233@N06",	"UW Digital Collections"),
        ("88669438@N03",	"Fotoarkivet NTM"),
        ("9189488@N02",	"Ljósmyndasafn Reykjavíkur / Reykjavík Museum of"),
        ("94021017@N05",	"National Archives of Estonia"),
        ("94268151@N07",	"Local History & Archives, Hamilton Public Library"),
        ("95711690@N03",	"Provincial Archives of Alberta"),
        ("95717549@N07",	"UL Digital Library"),
        ("95772747@N07",	"National Museum of Denmark"),
        ("98304311@N03",	"Regionaal Archief Alkmaar Commons"),
        ("98726691@N05",	"Port Morien Digital Archive"),
        ("99115493@N08",	"Sinaloa Fotografías Históricas"),
        ("99278405@N04",	"California Historical Society Digital Collection"),
        ("99902797@N03",	"Schlesinger Library, RIAS, Harvard University"),

        
        ### AVOIDED
        # ("49487266@N07",	"San Diego Air & Space Museum Archives"),
        # ("11334970@N05",	"Royal Museums Greenwich"),
        # ("200049760@N08",	"CommonsTestAccount"),
        # ("201268704@N06",	"CommonsPrivacyTest"),
    ]

    flickr = get_flickr_endpoint()
    conn = get_db_connection() 
    for nsid, name in institutions:
        get_public_photos(owner_nsid=nsid, conn=conn, flickr=flickr, owner_name=name)
    conn.close() 


