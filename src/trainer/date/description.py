import pandas as pd
def predict_date(description: str) -> int:
    date = 1850
    if description == 'taken in 2020':
        date = 2020
    return date

def explore(df: pd.DataFrame):


    pass