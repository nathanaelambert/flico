from sqlalchemy import text
import pandas as pd
import re
from pathlib import Path
import tempfile
import matplotlib.pyplot as plt

import matplotlib.pyplot as plt
from src.core.db import get_engine
from src.utils.format import large_number_for_display

if __name__ == "__main__":
    query = text("""--sql
        SELECT * FROM photo AS P
        JOIN machine_learning_photo AS MLP 
        ON P.owner_nsid = MLP.owner_nsid AND P.id = MLP.id
        WHERE p_building_given_descr is not null
    """)
    df = pd.read_sql_query(query, get_engine("server"))
    df = df.loc[:, ~df.columns.duplicated()]
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.max_colwidth', None)
    pd.set_option('display.width', None)
    pd.set_option('display.expand_frame_repr', False)
    df['page'] = df.apply(lambda r : f"https://www.flickr.com/photos/{r['owner_nsid']}/{r['id']}", axis=1 )
    df['year'] = pd.to_datetime(df['date_taken'], errors='coerce').dt.year


    # Plot distribution
    value_counts = df['p_building_given_descr'].value_counts().sort_index()

    plt.figure(figsize=(10, 6))
    value_counts.plot(kind='bar')

    plt.xlabel('p_building_given_descr')
    plt.ylabel('Count')
    plt.title('Distribution of p_building_given_descr')
    plt.tight_layout()

    # Save to temp file in current folder
    tmp_file = tempfile.NamedTemporaryFile(
        suffix=".png",
        dir=".",
        delete=False
    )

    plt.savefig(tmp_file.name)
    plt.close()

    print(f"Saved plot to: {Path(tmp_file.name).resolve()}")