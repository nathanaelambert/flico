from tqdm import tqdm
from sqlalchemy import text
import pandas as pd
import re

from src.core.db import get_engine
from src.trainer.db import update_ml_photo

SCORE_ENTRIES = {
    #positive
    "architectur*"   : +30,
    "residen*"       : +30,
    "château*"       : +40,
    "highway*"       : +10,
    "street*"        : +30,
    "avenue*"        : +20,
    "city"           : +7,           
    "built"          : +50,
    "build*"         : +70,
    "house*"         : +50,
    "home*"          : +50,
    "tower*"         : +25,
    "*toren"         : +25,
    "tour"           : +25,
    "church*"        : +45,
    "*kerk"          : +20,
    "cathedral*"     : +45,
    "temple*"        : +50,
    "station*"       : +45,
    "st."            : +20,
    "saint*"         : +20,
    "memorial*"      : +15,    
    "block*"         : +20,
    "near"           : +15,
    "village*"       : +10,
    "façade"         : +50,
    "facade"         : +50,
    "town*"          : +10,
    "*ville"         : +10,
    "wall*"          : +2,
    "area*"          : +4,
    "view of"        : +6,
    "vue"            : +6,
    "view from"      : +4,
    "outside"        : +3,
    "at"             : +3,
    "window*"        : +25,
    "porche*"        : +25,
    "door*"          : +10,
    "*institu*"      : +5,
    "bridge*"        : +2,
    "*berg*"         : +5,
    "place"          : +70,
    "sted"           : +40,
    "gate"           : +40,
    "plass"          : +25,
    "kommune"        : +2,
    "*hotel*"        : +50,  
    "monument*"      : +30,
    "parc"           : +10,
    "moulin"         : +5,
    "statue"         : +40,
    "tombe*"         : +30,
        






    #negative
    "born"           : -50,
    "scene*"         : -10,
    "construction*"  : -50,
    "demolition*"    : -40,
    "fire*"          : -30,  
    "ship*"          : -100,
    "*plan"          : -40,
    "harbour*"       : -40,
    "gun*"           : -20,
    "fight*"         : -15,
    "port*"          : -30,
    "surf"           : -150,
    "train*"         : -50,
    "locomotive*"    : -100,
    "*tunnel*"       : -50,
    "*banen"         : -50,
    "rail*"          : -50,
    "wagon*"         : -30,
    "portrait*"      : -100,
    "portrett"       : -100,
    "pose*"          : -50,
    "uniform*"       : -20,
    "wear*"          : -30,
    "famil*"         : -50,
    "guest*"         : -40,
    "team*"          : -30,
    "member*"        : -40,
    "group*"         : -10,
    "dress*"         : -20,
    "child*"         : -20,
    "mother"         : -50,
    "girl*"          : -40,
    "boy*"           : -40,
    "animal*"        : -30,
    "*broeder*"      : -40,
    "young"          : -40,
    "falls"          : -30,
    "garden"         : -30,
    "show*"          : -30,
    "plan"           : -100,
    "sketch*"        : -100,
    "map"            : -100,
    "amendment*"     : -150,
    "publish*"       : -10,
    "statsakt*"      : -50,
    "constitution*"  : -150,
    "meet*"          : -30,
    "*tevnet*"       : -30,
    "house of representa*": -100,
    "house of common*": -100,
    "gorge*"         : -50,
    "ice"            : -40,
    "bois"           : -40,
    "inhabited"      : -150,
    "wood*"          : -40,
    "tree*"          : -50,
    "hole*"          : -30,
    "exhibit*"       : -5,
    "*stelling"      : -5,
    "chaplian"       : -20,
    "*ker"           : -15,
    "*kers"          : -15,
    "draft*"         : -40,
    "furniture*"     : -40,
    "day"            : -40,
    "president"      : -150,
    "worker*"        : -50,
    "white house"    : -100,
    "chamber"        : -50,
    "office"         : -40,
    "room"           : -100,

}

def predict_is_building_given_descr(): 

    query = text("""--sql
        SELECT * FROM photo AS P
        JOIN machine_learning_photo AS MLP 
        ON P.owner_nsid = MLP.owner_nsid AND P.id = MLP.id
        WHERE P.latitude IS NOT NULL
        AND P.longitude IS NOT NULL
        AND P.latitude  != 0
        AND P.longitude != 0
    """)
    df = pd.read_sql_query(query, get_engine("trainer"))
    df = df.loc[:, ~df.columns.duplicated()]

    tqdm.pandas()

    df['building_score'] = df.progress_apply(
        lambda row: sum(
            score
            for keyword, score in SCORE_ENTRIES.items()
            if re.search(
                _keyword_to_regex(keyword),
                (
                    str(row['title']) +
                    str(row['description'])
                ).lower()
            )
        ),
        axis=1
    )
    min_score = abs(sum(score for score in SCORE_ENTRIES.values() if score < 0))
    max_score = sum(score for score in SCORE_ENTRIES.values() if score > 0)
    df['p_building_given_descr'] = df.apply(lambda row: 
        (row['building_score'] + min_score + 1) / (max_score + min_score + 2)
        , axis=1
    )
    update_ml_photo(df, 'p_building_given_descr')


def _keyword_to_regex(k):
    k = k.lower().strip()
    if k.startswith("*") and k.endswith("*") and len(k) > 2:
        core = re.escape(k[1:-1])
        return rf"{core}"
    elif k.startswith("*"):
        core = re.escape(k[1:])
        return rf"{core}(?![a-z])"
    elif k.endswith("*"):
        core = re.escape(k[:-1])
        return rf"{core}"
    else:
        core = re.escape(k)
        return rf"(?<![a-z]){core}(?![a-z])"

def _display_score(df):
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', None)
    pd.set_option('display.expand_frame_repr', False)
    df['page'] = df.apply(lambda r : f"https://www.flickr.com/photos/{r['owner_nsid']}/{r['id']}", axis=1 )
    df['year'] = pd.to_datetime(df['date_taken'], errors='coerce').dt.year
    columns = [
        'page',
        'building_score',
        # 'reg_n_pred_date',
        # 'descr_score',
        #  'descr_pred_date', 
        #  'year', 
    ]
    # df = df[df['building_score'] == 0]
    # print(df[columns].head(50))
    print(df[columns].sort_values(by='building_score', ascending=False).head(50))

