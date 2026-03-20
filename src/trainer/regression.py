import pandas as pd
import numpy as np
import ast
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error
from datetime import datetime
from ..postgresql.connector import get_db_connection

def get_data():
    engine = get_db_connection("trainer")
    query = """
        SELECT mlp.owner_nsid, mlp.id, mlp.sig_lip_vect_n, mlp.is_test_set,
               p.url_n, p.date_taken, p.date_taken_granularity,
               p.title, p.description
        FROM machine_learning_photo mlp
        JOIN photo p ON (p.owner_nsid, p.id) = (mlp.owner_nsid, mlp.id)
        WHERE mlp.sig_lip_vect_n IS NOT NULL
    """
    photos = pd.read_sql_query(query, engine)
    photos['year'] = pd.to_datetime(photos['date_taken'], errors='coerce').dt.year
    train = photos[photos["is_test_set"] == False]
    test = photos[photos["is_test_set"] == True]

    return train.reset_index(drop=True), test.reset_index(drop=True)

def date_taken_regression(train):
    X = np.stack(train["sig_lip_vect_n"].values)
    y = train["year"]
    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    mae = mean_absolute_error(y, y_pred)
    print(f"Train  MeanAbsoluteError: {round(mae, 2)} years")
    return model, mae

def random_baseline(train):
    np.random.seed(42)
    random_preds = np.random.randint(1850, 2027, size=len(train))
    mae_random = mean_absolute_error(train["year"], random_preds)
    print(f"Random MeanAbsoluteError: {round(mae_random,2)} years")  # Should be ~44
    return mae_random

def evaluate(model, test):
    X_test = np.stack(test["sig_lip_vect_n"].values)
    y_test = test["year"]
    y_pred = model.predict(X_test)
    test = test.copy()
    test["prediction"] = y_pred
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Test   MeanAbsoluteError: {round(mae, 2)} years")
    return test, {"mae": mae}

if __name__ == "__main__":
    train, test = get_data()
    model, train_error = date_taken_regression(train)
    mae_random = random_baseline(train)
    test_with_preds, metrics = evaluate(model, test)

    """ RESULTS:
    Train  MeanAbsoluteError: 24.98 years
    Random MeanAbsoluteError: 57.59 years
    Test   MeanAbsoluteError: 25.45 years
    """