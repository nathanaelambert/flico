from pathlib import Path
import pandas as pd
import gc
from typing import Optional
from dataclasses import dataclass
from tqdm import tqdm

from ...core.db import get_photos_where
from ..db import update_ml_photo

def combined_predictions():
    last_id = load_last_id()
    for i in tqdm(range(300), desc='description', total=300, unit='batch'):
        last_id = _process_a_batch(last_id)
        if last_id is None:
            break

        save_last_id(last_id)
        
def _process_a_batch(last_id):
    df = get_photos_where(user="trainer", clause=f"""--sql
        WHERE mlp.id > {last_id}
        ORDER BY mlp.id
        LIMIT 10000
    """)

    if df.empty:
        return None

    max_id = df["id"].max()
    
    df['year_taken'] = pd.to_datetime(df['date_taken'], errors='coerce').dt.year
    if df.empty:
        return df
        
    df['corrected_year'] = df.apply(
        lambda row: process_date(Date(
            reg_n_pred_date  = row['reg_n_pred_date'],
            descr_pred_date  = row['descr_pred_date'],
            descr_pred_date_1= row['descr_pred_date_1'],
            descr_pred_date_2= row['descr_pred_date_2'],
            p_descr_date     = row['p_descr_date'],
            p_descr_date_1   = row['p_descr_date_1'],
            p_descr_date_2   = row['p_descr_date_2'],
            year_taken       = row['year_taken'],
            human_pred_date  = row['human_pred_date'],
        )), 
        axis=1
    )
    df = df[df['corrected_year'].notna()]
    update_ml_photo(df, 'corrected_year')

    del df
    gc.collect()
    return max_id

@dataclass
class Date:
    reg_n_pred_date: Optional[int]
    descr_pred_date: Optional[int]
    descr_pred_date_1: Optional[int]
    descr_pred_date_2: Optional[int]
    p_descr_date: Optional[float]
    p_descr_date_1: Optional[float]
    p_descr_date_2: Optional[float]
    year_taken: Optional[int]
    human_pred_date: Optional[int]

    
def process_date(d: Date, min_p = 0.69, year_threshold=5) -> Optional[int]:
    p = d.p_descr_date or 0
    p1 = d.p_descr_date_1 or 0
    p2 = d.p_descr_date_2 or 0
    if d.human_pred_date is not None and d.human_pred_date > 0:
        return d.human_pred_date # added after evaluation
    if (
        d.year_taken is not None 
        and d.descr_pred_date is not None 
        and d.year_taken == d.descr_pred_date
    ):
        return d.year_taken
    if p > min_p and d.descr_pred_date is not None:
        dates = [d.descr_pred_date]
        if p1 > min_p and d.descr_pred_date_1 is not None:
            dates.append(d.descr_pred_date_1)
        if p2 > min_p and d.descr_pred_date_2 is not None:
            dates.append(d.descr_pred_date_2)
        lower_bound = min(dates)
        upper_bound = max(dates)
        if (d.year_taken is not None 
            and lower_bound <= d.year_taken <= upper_bound
            and upper_bound - lower_bound < 2 * year_threshold
        ):
            return d.year_taken
        if upper_bound - lower_bound <= year_threshold:
            return round((upper_bound + lower_bound) / 2)
        if (
            d.reg_n_pred_date is not None
            and lower_bound <= d.reg_n_pred_date <= upper_bound
            and upper_bound - lower_bound < 2 * year_threshold
        ):
            return d.reg_n_pred_date
    if (
        d.descr_pred_date is not None
        and d.reg_n_pred_date is not None
        and d.descr_pred_date == d.reg_n_pred_date
    ):
        return d.descr_pred_date
    if (
        d.reg_n_pred_date is not None
        and d.year_taken is not None
        and d.year_taken == d.reg_n_pred_date
    ):
        return d.year_taken
    return None


CHECKPOINT = Path("last_id.txt")

def load_last_id():
    if CHECKPOINT.exists():
        return int(CHECKPOINT.read_text())
    return 0

def save_last_id(last_id):
    CHECKPOINT.write_text(str(last_id))  


    

"""
SUSPICISOUS WRONG DATE:

intenet book archive 1825

san diego plane numbers

navy medicine stupid numbers


if more than 1 descr pred date: and date_taken in range,
combined = date_taken
https://www.flickr.com/photos/32605636@N06/8887561472

"""