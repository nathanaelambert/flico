import pandas as pd
import pandera.pandas as pa
from src.trainer.db import PhotoId
from src.server.db import Photo

def filter(photos: pa.typing.DataFrame[Photo]) -> pa.typing.DataFrame[PhotoId]:
    """This code is responsible for providing a balanced dataset with accurate dates.
    The main problem encoutered so far (march 31st 2026) is identifying and filtering out
    pictures with innacurate date_taken. A lot of old pictures scanned or aquired in the 2000s
    have a recent date_taken, despite being taken in the past. Pictures before 2000 are of good
    quality.
    """
    photos['year'] = pd.to_datetime(df['date_taken'], errors='coerce').dt.year
    filtered_df = photos.dropna(subset=['year'])
    filtered_df = filtered_df[(filtered_df['year'] >= 1850) & (filtered_df['year'] <= 2026)]
    # filtering the british library because all their dates are 2013 (unreliable dates)
    filtered_df = filtered_df[filtered_df['owner_nsid'] != '12403504@N02']
    df_500 = _sample_by_year(filtered_df, 500)
    return df_500[['owner_nsid', 'id']]

def _sample_by_year(df, max_per_year=500):
    """
    Sample max_per_year photos for each year prioritizing:
    1. Lowest granularity first (take all until limit reached)
    2. Maximum uniform owner distribution in the critical granularity level

    Granularity is supposed to be a precision indicator of the metadata
    More diversity of owners probably means less geographical bias
    Limiting each year to 500 pics because there is a lot of recent pics and a few old ones
    """
    sampled_dfs = []   
    for year, group in df.groupby('year'):
        if len(group) > max_per_year:
            sampled = sampled = _sample_uniform_low_granularity(group, max_per_year)
            sampled_dfs.append(sampled)
        else:
            sampled_dfs.append(group)  
    sampled_df = pd.concat(sampled_dfs, ignore_index=True)
    print(f"Sampled {len(sampled_df):,} photos spanning {int(sampled_df['year'].min())}–{int(sampled_df['year'].max())}")
    return sampled_df

def _sample_uniform_low_granularity(year_group, max_per_year):
    sampled = []
    remaining = max_per_year
    sorted_group = year_group.sort_values('date_taken_granularity')
    gran_levels = sorted(sorted_group['date_taken_granularity'].unique())
    for gran in gran_levels:
        level_group = sorted_group[sorted_group['date_taken_granularity'] == gran]
        if len(sampled) + len(level_group) <= remaining:
            sampled.append(level_group)
            remaining -= len(level_group)
            if remaining <= 0:
                print(f"Error: sampled too much remaining: {remaining}")
                break
        else:
            critical_sample = _sample_uniform_owners(level_group, remaining)
            sampled.append(critical_sample)
            remaining = 0
            break
        
    return pd.concat(sampled, ignore_index=True)

def _sample_uniform_owners(subgroup, target_count):
    owner_sizes = subgroup.groupby('owner_nsid').size().sort_values()
    total_owners = len(owner_sizes)
    sampled = []
    remaining_target = target_count
    for i, (owner_nsid, size) in enumerate(owner_sizes.items()):
        remaining_owners = total_owners - i
        fair_share = remaining_target // remaining_owners
        take = min(size, fair_share)
        owner_photos = subgroup[subgroup['owner_nsid'] == owner_nsid]
        sampled.append(owner_photos.sample(n=take))
        remaining_target -= take 
    return pd.concat(sampled, ignore_index=True)

