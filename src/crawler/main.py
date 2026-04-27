import pandas as pd
import src.utils.colors as c
from src.utils.flickr import INSTITUTIONS
from src.utils.format import large_number_for_display
import src.crawler.flickr as flickr
from src.crawler.db import insert_institution, insert_license, insert_picture
from src.server.db import count_flickr


def crawl_institutions():
    for inst in flickr.institutions(): 
        insert_institution(inst)

def crawl_licenses():
    for license in flickr.licenses():
        insert_license(license)

def crawl_pictures(owner_nsid: int, owner_name: str, start_page=1):
    pages = flickr.pictures(owner_nsid, 1)['pages']
    for page in range(max(1, min(start_page, pages - 1)), pages):
        pics_saved = 0
        for photo in flickr.pictures(owner_nsid, page)['photo']:

            try:
                if insert_picture(photo):
                    pics_saved += 1
            except Exception as e:
                error = f"{c.RED}Photo {photo['id']} from {owner_name}: {e}{c.RESET}"
                print(error)
                print(error, file=open(error_log.txt, 'a'))
            
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
        crawl_pictures(nsid, name, 300)

def get_stats(df=count_flickr()):
    df['flickr'] = ''
    grand_total = 0
    for nsid, institution in INSTITUTIONS:
        on_flickr = flickr.pictures(nsid, 1)['total']
        grand_total += on_flickr
        df.loc[df['institution'] == institution, 'flickr'] = large_number_for_display(on_flickr)
    df.loc[df['institution'] == 'TOTAL', 'flickr'] = large_number_for_display(grand_total)
    print(df)
    return df

if __name__ == "__main__":
    # crawl_institutions()
    # crawl_licenses()
    crawl_pictures_from_all_institutions()
    # get_stats()

    # crawl_pictures("8623220@N02",	"The Library of Congress")