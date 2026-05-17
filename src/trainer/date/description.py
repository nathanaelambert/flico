import pandas as pd
import re
from collections import defaultdict, Counter
from statistics import mean
from typing import Optional
import numpy as np

def predictions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['date_upload_year'] = pd.to_datetime(df['date_upload'], unit='s').dt.year
    df = df[df['descr_pred_date'].isna()]
    if df.empty:
        return df
    results = df.apply(
        lambda row: _predict_date(row['description'], row['title'], row['date_upload_year']), 
        axis=1
    )
    df[["descr_pred_date", "descr_score"]] = pd.DataFrame(results.tolist(), index=df.index)
    return df

def isSerial(word: str) -> bool:
    if '_' in word:
        return True
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
            for pattern in [r'^[12]\d{3}$', r'^\d{1}$', r'^[012]\d{1}$', r''])
            for part in parts
    )
    """
    errors: 
    "Eph-E-DRAMA-1899-01." -> True
    """
        

def _predict_date(description: str, title: str, date_uploaded: int) -> tuple[Optional[int], int]: 
    """
    Assigns a score to each candidate date (4 consecutive digits) in the description and title based on ad hoc patterns.
    Return dates with the best score, average amongst candidates to break ties.
    Might return None if no satisfying candidate is found.
    """
    def _extract_candidate_with_context(text):
        return [
            {   'year': int(m.group()), 'full_text': text,
                'line': line, 'sentence': sentence, 'word': word,
                'start': m.start(), 'end': m.end(),
            } 
            for line in text.splitlines()
            for sentence in re.split(r'\. |; |\? |: |, |—', line)
            for word in sentence.split(' ')
            for m in re.finditer(r'(?<![A-Za-z0-9_])[12]\d{3}(?![0-9])', word)
        ]
    
    description = re.sub(r'(?<!\d)(\d{3})?-\?', r'\g<1>5', description) # Optional: approximate decade to midpoint

    all_matches = [
        {**m, 'source': 'description'} for m in _extract_candidate_with_context(description or "")
    ] + [
        {**m, 'source': 'title'} for m in _extract_candidate_with_context(title or "")
    ]

    all_matches = [m for m in all_matches if m['year'] <= date_uploaded]
    if not all_matches:
        return None, 0

    patterns = lambda m, years: {
        # reward positive patterns
        'end_of_line': max(0, 20 - (len(m['line']) - m['end'])),
        'start_of_line': max(0, 15 - m['start']),
        'bracket_before': 23 if m['line'][max(0, m['start'] - 2):m['start']].endswith(('[', '[ ')) else 0,
        'bracket_after': 24 if m['line'][m['end']:min(len(m['line']), m['end'] + 2)].startswith((']', ' ]')) else 0,
        'parenth_before': 12 if m['line'][max(0, m['start'] - 2):m['start']].endswith(('(', '( ')) else 0,
        'parenth_after': 13 if m['line'][m['end']:min(len(m['line']), m['end'] + 2)].startswith((')', ' )')) else 0,
        'single_on_line': 10 if (dates := re.findall(r'\d{4}', m['line'])) and len(dates) == 1 and dates[0] == str(m['year']) else 0,
        'in_title': 5 if m.get('source') == 'title' else 0,
        'has_smaller_in_description': 8 if years and m['year'] > min(years) else 0,
        'has_bigger_in_description': 8 if years and m['year'] < max(years) else 0,
        'has_date_on_line': 21 if 'date' in m['line'].lower() else 0,
        'probable_range': 30 * np.exp(-((1925 - m['year']) ** 2) / (2 * 150 ** 2)),
        # punish negative patterns
        'serial_numbers' : -80 if isSerial(m['word']) else 0,
        'PX': -40 if 'PX' in m['line'] else 0,
        'number': -50 if 'number' in m['line'].lower() else 0,
        "dollar": -50 if '$' in m['sentence'] else 0,


        #Navy Medicine is annoying with their stupid meaning less titles that look like dates
        # https://www.flickr.com/photos/61270229@N05/54791908741
        # 'punish_serial_number': -100 if re.search(r'\d{5}', m['sentence']) else 0,
        #'punish_serial_number_0': -100 if re.search(r'(?<![0-9]0\d{1})', m['sentence']) else 0,
        # 'punish_serial_url': -100 if '/' in m['line']  and '.' in m['line'] else 0, 
        #'underscore_before': -30 if m['line'][max(0, m['start'] - 2):m['start']].endswith('_') else 0,
        #'underscore_after': -30 if m['line'][m['end']:min(len(m['line']), m['end'] + 2)].startswith('_') else 0,
    }

    years_in_desc = [m['year'] for m in all_matches if m['source'] == 'description']
    scored_matches = [{'match': m, 'score_by_pattern': p, 'total_score': sum(p.values())} 
                      for m, p in [(m, patterns(m, years_in_desc)) for m in all_matches]]

    if not scored_matches:
        return None, 0

    top_scored = max(scored_matches, key=lambda x: x['total_score'])
    if top_scored['total_score'] < 5:
        return None, top_scored['total_score']
    top_matches = [m for m in scored_matches if m['total_score'] == top_scored['total_score']]
    top_years = sorted({m['match']['year'] for m in top_matches})

    prdy =  top_years[0] if len(top_years) == 1 else int(round(mean(top_years)))
    return int(prdy), top_scored['total_score']
"""
Technically returns the wrong date, but I will do  nothing about it:
https://www.flickr.com/photos/134017397@N03/26282016448 "Aug. 24 1003" -> 1003
https://www.flickr.com/photos/47290943@N03/48749615926  "NLI Ref: POOLEWP 1008" -> 1008
https://www.flickr.com/photos/150408343@N02/34585529631 "1017 - LEFT" -> 1017
https://www.flickr.com/photos/164711667@N06/54200824785 "1033 Lenore Street, Lansing" -> 1033
https://www.flickr.com/photos/29454428@N08/6940033955   "ca.1883-1930s, PXE 1028," -> 1028


Is also a failure but I have good reasons to keep it:
https://www.flickr.com/photos/61270229@N05/49362869843  "NOB (NH)-KWST 1077." -> 1077 (other date looks like context)











FAILED ON (RETURNED WRONG DATE):
https://www.flickr.com/photos/61270229@N05/54793754139
https://www.flickr.com/photos/134017397@N03/54151877913 ??


https://www.flickr.com/photos/32605636@N06/54787514482 ( hdl.handle.net/10462/deriv/0000. -> 0)
https://www.flickr.com/photos/61270229@N05/52865270141 ( NAMRU San Antonio attends Fiesta San Antonio Activities 230424-N-ND850-0001 -> 1)



"""

"""
TO FIX :
Predicting dates for 79373 pictures.
       reg_n_pred_date  descr_score  descr_pred_date  year                                                     page
78585             1942         15.0              0.0  2025   https://www.flickr.com/photos/32605636@N06/54787514482
825               1954         15.0              0.0  2024   https://www.flickr.com/photos/32605636@N06/53485137292
3874              1953         15.0              0.0  2024   https://www.flickr.com/photos/32605636@N06/53486458095
3877              1936         16.0              0.0  2023   https://www.flickr.com/photos/32605636@N06/53011859441
3875              1931         16.0              0.0  2023   https://www.flickr.com/photos/32605636@N06/53011273692
79137             1900         15.0              0.0  2023   https://www.flickr.com/photos/32605636@N06/53346085926
2106              1911         15.0              0.0  2023   https://www.flickr.com/photos/32605636@N06/53345206397
3876              1965         16.0              0.0  2023   https://www.flickr.com/photos/32605636@N06/53012237850
78794             1944         15.0              0.0  2022   https://www.flickr.com/photos/32605636@N06/51961605694
4597              1950         15.0              0.0  2021   https://www.flickr.com/photos/32605636@N06/51502469361
2242              2022         25.0              2.0  2022   https://www.flickr.com/photos/61270229@N05/51940361669
15113             1919         20.0              1.0  2020   https://www.flickr.com/photos/37547255@N08/51080649478
2589              2021         25.0              4.0  2021   https://www.flickr.com/photos/61270229@N05/51163248037
2                 1943         25.0              1.0  2015  https://www.flickr.com/photos/201627032@N02/54118592662
1                 1984         25.0              1.0  2015  https://www.flickr.com/photos/201627032@N02/54119904925
14985             1971         25.0              1.0  2015  https://www.flickr.com/photos/201627032@N02/54119783074
3843              1937         37.0             12.0  2025   https://www.flickr.com/photos/32605636@N06/54660511838
15167             1926         31.0              8.0  2021   https://www.flickr.com/photos/37547255@N08/51081438507
7                 2011         25.0              9.0  2021   https://www.flickr.com/photos/99115493@N08/51433527451
4598              1945         37.0             13.0  2025   https://www.flickr.com/photos/32605636@N06/54660511823
8                 1995         25.0             10.0  2021   https://www.flickr.com/photos/99115493@N08/51434494470
78768             1979         16.0              5.0  2015  https://www.flickr.com/photos/124448282@N08/19750252484
9                 1989         25.0             11.0  2021   https://www.flickr.com/photos/99115493@N08/51434494380
12                1994         25.0             12.0  2021   https://www.flickr.com/photos/99115493@N08/51434268499
3                 1932         31.0             11.0  2020   https://www.flickr.com/photos/37547255@N08/51081438477
392               1966         20.0              3.0  2011    https://www.flickr.com/photos/37381115@N04/5852241847
22                2003         25.0             13.0  2021   https://www.flickr.com/photos/99115493@N08/51434494330
71799             1955         31.0             12.0  2019   https://www.flickr.com/photos/37547255@N08/51081347726
24                1960         37.0             18.0  2025   https://www.flickr.com/photos/32605636@N06/54660511658
1297              1933         37.0             20.0  2025   https://www.flickr.com/photos/32605636@N06/54660511638
762               2000          7.0             14.0  2016  https://www.flickr.com/photos/135637350@N04/28724571814
71800             1951         31.0             19.0  2021   https://www.flickr.com/photos/37547255@N08/51080649633
3844              1948         37.0             24.0  2025   https://www.flickr.com/photos/32605636@N06/54660289041
824               1948         31.0             19.0  2019   https://www.flickr.com/photos/37547255@N08/51080651053
1006              1947         31.0             20.0  2019   https://www.flickr.com/photos/37547255@N08/51012162030
4763              1937         24.0             21.0  2020   https://www.flickr.com/photos/37547255@N08/51080650413
56761             2020         45.0             23.0  2021   https://www.flickr.com/photos/61270229@N05/51062860471
3203              2015         28.0             20.0  2016  https://www.flickr.com/photos/135637350@N04/28771203304
15307             1927         37.0             29.0  2024   https://www.flickr.com/photos/32605636@N06/53560775591
71801             1951         31.0             25.0  2019   https://www.flickr.com/photos/37547255@N08/51080650968
4889              1966         41.0             29.0  2022   https://www.flickr.com/photos/61270229@N05/51889826833
71796             1911         37.0             36.0  2025   https://www.flickr.com/photos/32605636@N06/54660517689
1772              1942         37.0             36.0  2025   https://www.flickr.com/photos/32605636@N06/54659448792
15280             1924         37.0             36.0  2024   https://www.flickr.com/photos/32605636@N06/53559915927
2320              1924         37.0             37.0  2025   https://www.flickr.com/photos/32605636@N06/54659448737
361               1954         34.0             29.0  2015   https://www.flickr.com/photos/61270229@N05/29281756066
2590              1970         33.0             38.0  2022   https://www.flickr.com/photos/61270229@N05/51989237029
4103              1934         30.0             36.0  2019   https://www.flickr.com/photos/37547255@N08/51080650863
12449             1971         40.0              2.0  1984   https://www.flickr.com/photos/61270229@N05/53861205198
1482              1932         37.0             43.0  2025   https://www.flickr.com/photos/32605636@N06/54659448652
Updated column 'descr_pred_date' : 71860 rows affected.
"""