from sqlalchemy import text
import pandas as pd
import re


from src.core.db import get_engine
from src.utils.format import large_number_for_display

if __name__ == "__main__":
    query = text("""--sql
        SELECT * FROM photo AS P
        JOIN machine_learning_photo AS MLP 
        ON P.owner_nsid = MLP.owner_nsid AND P.id = MLP.id
        WHERE P.latitude IS NOT NULL
        AND P.longitude IS NOT NULL
        AND P.latitude  != 0
        AND P.longitude != 0
        ORDER BY RANDOM()
        LIMIT 500
    """)
    df = pd.read_sql_query(query, get_engine("server"))
    df = df.loc[:, ~df.columns.duplicated()]

    score_entries = {
        #positive
        "architectur"   : +30,
        "château"       :+40,
        "highway"       : +10,
        "street"        : +20,
        "avenue"        : +20,
        "built"         : +50,
        "build"         : +70,
        "house"         : +50,
        "home"          :+50,
        "tower"         : +25,
        "church"        : +45,
        "cathedral"     : +45,
        "st."           : +20,
        "saint"         : +20,
        "memorial"      : +15,    
        "block"         : +20,
        "near"          : +15,
        "village"       : +10,
        "town"          : +10,
        "wall"          : +2,
        "area"          : +4,
        "view of"       : +6,
        "view from"     : +4,
        "outside"       : +3,
        "at"            : +3,
        "windows"       : +25,
        "porches"       : +25,
        "door"          : +10,

    
        #negative
        "born"          : -50,
        "scene"         : -10,
        "ship"          : -100,
        "harbour"       : -40,
        "port"          : -30,
        "train"         : -50,
        "locomotive"    : -100,
        "rail"          : -50,
        "portrait"      : -100,
        "pose"          : -50,
        "uniform"       : -20,
        "family"        : -50,
        "team"          : -30,
        "dress"         : -20,
        "child"         : -20,
        "young"         : -40,
        "falls"         : -30,
        "show"          : -30,
        "plan"          : -100,
        "map"           : -100,
        "amendment"     : -150,
        "constitution"  : -150,
        "house of representa": -100,
        "house of common": -100,

    }

    df['building_score'] = df.apply(
        lambda row: sum(
            score
            for keyword, score in score_entries.items()
            if re.search(
                rf'(?<![a-z]){re.escape(keyword)}',
                (
                    str(row['title']) +
                    str(row['description'])
                ).lower()
            )
        ),
        axis=1
    )
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
    print(df[columns].sort_values(by='building_score', ascending=True).head(50))

