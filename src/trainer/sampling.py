import numpy as np
import pandas as pd

def sample_by_year(df, max_per_year=500):
    """
    Sample max_per_year photos for each year prioritizing:
    1. Lowest granularity first (take all until limit reached)
    2. Maximum uniform owner distribution in the critical granularity level
    """
    sampled_dfs = []   
    for year, group in df.groupby('year'):
        if len(group) > max_per_year:
            sampled = sampled = _sample_uniform_low_granularity(group, max_per_year)
            sampled_dfs.append(sampled)
        else:
            sampled_dfs.append(group)
    return pd.concat(sampled_dfs, ignore_index=True)

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

