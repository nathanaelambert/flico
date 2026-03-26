import src.utils.colors as c
from src.utils.flickr import INSTITUTIONS
from src.crawler.flickr import institutions, licenses, pictures
from src.crawler.db import insert_institution, insert_license, insert_picture
    
def crawl_institutions():
    for inst in institutions(): 
        insert_institution(inst)

def crawl_licenses():
    for license in licenses():
        insert_license(license)

def crawl_pictures(owner_nsid: int, owner_name: str, start_page=1):
    pages = pictures(owner_nsid, 1)['pages']
    for page in range(max(1, min(start_page, pages - 1)), pages):
        pics_saved = 0
        for photo in pictures(owner_nsid, page)['photo']:
            try:
                if insert_picture(photo):
                    pics_saved += 1
            except Exception as e:
                print(f"{c.RED}Photo {photo['id']}: {e}{c.RESET}")
            
        match pics_saved:
            case 500:
                color_pics = c.GREEN
            case 0:
                color_pics = c.GREY
            case _:
                color_pics = c.YELLOW
        print(f"{c.GREY}page {c.RESET}"
                f"{c.WHITE}{page:03d}{c.RESET}"
                f"{c.GREY} / {pages:03d} :{c.RESET} "
                f"{color_pics}{pics_saved:03d}{c.RESET}"
                f"{c.GREY} pics downloaded from {c.WHITE}{owner_name}{c.RESET}"
                f"{c.GREY}, {owner_nsid}{c.RESET}")

def crawl_pictures_from_all_institutions():
    for nsid, name in INSTITUTIONS:
        crawl_pictures(nsid, name)

if __name__ == "__main__":
    # crawl_institutions()
    # crawl_licenses()
    crawl_pictures_from_all_institutions()