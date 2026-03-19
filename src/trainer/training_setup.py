import pandas as pd
from sklearn.model_selection import train_test_split

from ..postgresql.connector import get_db_connection

from .data_processing import filter_dated_photos, get_dated_photos
from .sampling import sample_by_year

def populate_machine_learning_photo():
    """populate database with training and testing data
    returns dataframes of training and testing data"""
    df500 = sample_by_year(filter_dated_photos(get_dated_photos()), 500)
    engine = get_db_connection('trainer')

    df_train, df_test = train_test_split(
        df500[['owner_nsid', 'id']], 
        test_size=0.2, 
        random_state=42  # For reproducibility
    )
    df_train['is_test_set'] = False
    df_test['is_test_set'] = True

    df_train.to_sql(
        name='machine_learning_photo',
        con=engine,
        if_exists='append',
        index=False,
        method='multi',
        chunksize=1000
    )
    df_test.to_sql(
        name='machine_learning_photo',
        con=engine,
        if_exists='append',
        index=False,
        method='multi',
        chunksize=1000
    )
    return df_train, df_test


if __name__ == "__main__":
    pass
    # populate_machine_learning_photo()