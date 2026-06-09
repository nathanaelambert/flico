import pandas as pd
import re
from statistics import mean
from typing import Optional
from tqdm import tqdm
import numpy as np
import src.utils.colors as c
from ...core.db import get_photos_where
from ..db import rm_data_ml_photo, update_ml_photo
from concurrent.futures import ProcessPoolExecutor

def context_predictions(rm_existing=False):
    cols = ["descr_pred_date", "p_descr_date", 
        "descr_pred_date_1", "p_descr_date_1",
        "descr_pred_date_2", "p_descr_date_2"]
    if rm_existing:
        for col in cols:
            rm_data_ml_photo(col)
    for i in tqdm(range(300), desc='description', total=300, unit='batch'):
        _process_a_batch(cols)

def _process_a_batch(cols: list[str], silent=True):
    df = get_photos_where(user="trainer", clause="""--sql
        WHERE descr_pred_date is NULL
        ORDER BY RANDOM()
        LIMIT 10000
    """)
    
    df['date_upload_year'] = pd.to_datetime(df['date_upload'], unit='s').dt.year
    if df.empty:
        return df
        
    results = df.apply(
        lambda row: predict_dates(row['description'], row['title'], row['tags'], row['date_upload_year'], row['owner_nsid']), 
        axis=1
    )
    results = results.apply(lambda x: [None] * 6 if x is None else x)
    df[cols] = pd.DataFrame(results.tolist(), index=df.index)
    df = df.replace({np.nan: None})
    for col in cols:
        update_ml_photo(df, col)
    if not silent:
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_colwidth', None)
        pd.set_option('display.width', None)
        pd.set_option('display.expand_frame_repr', False)
        df['page'] = df.apply(lambda r : f"https://www.flickr.com/photos/{r['owner_nsid']}/{r['id']}", axis=1 )
        df['year'] = pd.to_datetime(df['date_taken'], errors='coerce').dt.year
        df["diff"] = (df["year"] - df["descr_pred_date"]).abs()
        df = df.sort_values("p_descr_date", ascending=True).drop(columns="diff")
        print(df[['reg_n_pred_date','p_descr_date', 'descr_pred_date', 'year', 'page', 
                'p_descr_date_1', 'descr_pred_date_1', 'p_descr_date_2', 'descr_pred_date_2']].head(50))
      

def predict_dates(description: str, title: str, tags: str, date_uploaded: int, owner_nsid: str) -> list[int | float]: 
    """
    Assigns a score to each candidate date (4 consecutive digits) in the description and title based on ad hoc PATTERNS.
    Return dictionnary key= candidate dates, values = probabilty of match
    Might return None if no satisfying candidate is found.
    """
    if owner_nsid == "99115493@N08":
        return None # WikiSinaloa has a bad habbit of having a stupid 4 digit number as title
    description = _sub_keywords(description)
    all_matches = _extract_four_digits_sequences_with_scores(description, title, tags, date_uploaded)
    if not all_matches:
        return None
    score_matches = _score_matches(all_matches)
    return _scores_to_proba_best_3(score_matches)


def _sub_keywords(description : str)-> str:
    description = re.sub(r'(?<!\d)(\d{3})?-\?', r'\g<1>5', description) # Optional: approximate decade to midpoint
    description = re.sub(r'(?<=\s)[Nn]o\.? ', 'Number', description)
    description = re.sub(r'(?<=\s)[Rr]ef\.? ', 'Reference', description)
    description = re.sub(r'(?<=\s)[cC]a?\.', 'Circa ', description)
    description = re.sub(r'\[(?:[cC]a?)\s*(\d{4})\]',  r'Circa \1',   description)

    description = re.sub(r'\d{3} - LEFT', 'garbage', description)
    return description

def _extract_candidate_with_context(text):
    return [
        {   'year': int(m.group()), 'full_text': text,
            'line': line, 'sentence': sentence, 'word': word,
            'start': m.start(), 'end': m.end(),
        } 
        for line in text.splitlines()
        for sentence in re.split(r'\.\s+|; |\? |, |—|>|<|\.\. |\.\.\. |\.(?=$)', line)
        for word in sentence.split(' ')
        for m in re.finditer(r'(?<![A-Za-z0-9_])[12]\d{3}(?![0-9])', word)
    ]

def _extract_four_digits_sequences_with_scores(description: str, title: str, tags: str, date_uploaded: int):
    all_matches = [
        {**m, 'source': 'description'} for m in _extract_candidate_with_context(description or "")
    ] + [
        {**m, 'source': 'title'} for m in _extract_candidate_with_context(title or "")
    ] + [
        {**m, 'source': 'tags'} for m in _extract_candidate_with_context(tags or "")
    ]
    return [m for m in all_matches if m['year'] <= date_uploaded]
    
def _score_matches(all_matches):
    PATTERNS = lambda m, years: {
        'bracket_before'            : +13 if m['word'].endswith(']') else 0,
        'bracket_after'             : +14 if m['word'].startswith('[') else 0,
        'parenth_before'            : +7 if m['word'].endswith(')') else 0,
        'parenth_after'             : +8 if m['word'].startswith('(') else 0,
        'single_on_line'            : +10 if (dates := re.findall(r'\d{4}', m['line'])) and len(dates) == 1 and dates[0] == str(m['year']) else 0,
        'in_title'                  : +5 if m.get('source') == 'title' else 0,
        'in_tags'                   : +12 if m.get('source') == 'tags' else 0,
        'has_smaller_in_description': +6 if years and m['year'] > min(years) else 0,
        'has_bigger_in_description' : +6 if years and m['year'] < max(years) else 0,
        'has_date_on_line'          : +28 if 'date' in m['line'].lower() else 0,
        'has_year_on_line'          : +28 if any(pat in m['line'].lower()     for pat in ['year', 'jaar', 'année']) else 0,
        'has_field'                 : +30 if any(pat in m['sentence'].lower() for pat in ['produced', 'published', 'created', 'taken']) else 0,
        'probable_range'            : +30 * np.exp(-((1925 - m['year']) ** 2) / (2 * 150 ** 2)),
        'circa'                     : +6 if 'circa' in m['sentence'].lower() else 0,
        # punish negative patterns
        'futuristic'                : -300 if m['year'] > 2030 else 0,
        'serial_numbers'            : -80 if _isSerial(m['word']) else 0,
        'PX'                        : -40 if 'PX' in m['sentence'] else 0,
        'CO'                        : -40 if 'CO' in m['sentence'] else 0, 
        'ref'                       : -40 if 'ref' in m['sentence'].lower() else 0,
        'donated'                   : -50 if any(pat in m['sentence'].lower() for pat in ['donated', 'donation', 'transfer', 'loaned']) else 0 ,
        'number'                    : -50 if any(pat in m['sentence'].lower() for pat in ['number', 'call']) else 0,
        "dollar"                    : -50 if '$' in m['sentence'] else 0,
        "street"                    : -40 if any(pat in m['sentence'].lower() for pat in['street', 'avenue', 'road', 'location']) else 0,
    }
    FILTER_THRESHOLD = 0
    return [
        {
            'match': m,
            'score_by_pattern': p,
            'total_score': sum(p.values())
        }
        for m in all_matches
        for p in [PATTERNS(m, [m['year'] for m in all_matches if m['source'] == 'description'])]
        if sum(p.values()) >= FILTER_THRESHOLD
    ]

def _isSerial(word: str) -> bool:
    if '_' in word:
        return True
    word = re.sub(r'[\[\]()]', '', word)
    if '-' in word:
        parts = word.split('-')
    elif '.' in word:
        parts = word.split('.')
    elif '/' in word:
        parts = word.split('/')
    else:
        return False
    if any(re.match(r'^[12]\d{2}s$', part) for part in parts):
        return False
    return len(parts) > 3 or not all(
        any(re.match(pattern, part) 
            for pattern in [r'^[12]\d{3}$', r'^\d{1}$', r'^[012]\d{1}$', r'^$'])
            for part in parts
    )
    """
    errors: 
    "Eph-E-DRAMA-1899-01." -> True
    """

def _scores_to_proba_best_3(scored_matches):
    grouped = {}
    for match in scored_matches:
        grouped.setdefault(match["match"]["year"], []).append(match["total_score"])
    
    combined_probas = {}
    for year, score_list in grouped.items():
        best_score = max(score_list)
        combined_non_zero_score = best_score + 2*len(score_list) + 100
        proba = max(0.0, min(0.9999, combined_non_zero_score/191))
        combined_probas[year] = proba
    
    ordered_probas = dict(sorted(combined_probas.items(), key=lambda i: i[1], reverse=True))
    flattened = [item for tup in list(ordered_probas.items())[:3] for item in tup]
    return flattened[:6] + [None] * max(0, 6 - len(flattened))







"""
Technically returns the wrong date, but I will do  nothing about it:
https://www.flickr.com/photos/134017397@N03/26282016448 "Aug. 24 1003" -> 1003
https://www.flickr.com/photos/47290943@N03/48749615926  "NLI Ref: POOLEWP 1008" -> 1008
https://www.flickr.com/photos/150408343@N02/34585529631 "1017 - LEFT" -> 1017
https://www.flickr.com/photos/164711667@N06/54200824785 "1033 Lenore Street, Lansing" -> 1033
https://www.flickr.com/photos/29454428@N08/6940033955   "ca.1883-1930s, PXE 1028," -> 1028


Is also a failure but I have good reasons to keep it:
https://www.flickr.com/photos/61270229@N05/49362869843  "NOB (NH)-KWST 1077." -> 1077 (other date looks like context)


bro, community archives...
https://www.flickr.com/photos/134017397@N03/28900993408 why do they put the date of donations and not the actual date
I guess I can't blame them bc they actually use the date_taken field correctly


this looks more like 1890 than 1930 to me.. but it's a debate
https://www.flickr.com/photos/32605636@N06/27247106097

Actually, this settles the debate:
https://www.flickr.com/photos/32605636@N06/4762679982
Queensland are trolling !! where did they get 1930 from ?


difficult range to extract to to spaces
https://www.flickr.com/photos/35740357@N03/7448555082
also combination of circa and range is common (also, date taken is approximated by 50 years)

ranges range
https://www.flickr.com/photos/41131493@N06/34300706301

TODO
MUST IMPROVE ON RANGES (now, often takes upper bound)
TODO
if final year is same as other that are punished return second best or None
TODO
add a rule where you we take the takendate from community archives of belleville hastings
134017397@N03

FAILED ON (RETURNED WRONG DATE):
https://www.flickr.com/photos/cabhc/42876755621/in/photostream/ -> 2008
https://www.flickr.com/photos/104959762@N04/52519816109 -> 2020

https://www.flickr.com/photos/126377022@N07/20527216764 -> 1980 (Check why not 1992 (in bracket, year kw)??)
"""