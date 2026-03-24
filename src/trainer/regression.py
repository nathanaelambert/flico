import joblib
import pandas as pd
import numpy as np
import ast
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.svm import SVR
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
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

    return photos, train.reset_index(drop=True), test.reset_index(drop=True)

def date_taken_train_model(train, model):
    X = np.stack(train["sig_lip_vect_n"].values)
    y = train["year"]
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

def save_predictions(model, photos):
    pass


if __name__ == "__main__":
    photos, train, test = get_data()

    # print("Random Benchmark:")
    # mae_random = random_baseline(train)
    """baseline random
    Random MeanAbsoluteError: 57.59 years
    """

    # print("Linear Regression:")
    # model_lin, mae_lin = date_taken_train_model(train, LinearRegression())
    # test_preds_lin, metrics_lin = evaluate(model_lin, test)
    """ RESULTS (march 20 2026):
    Train  MeanAbsoluteError: 24.98 years
    Test   MeanAbsoluteError: 25.45 years
    """

    # print("Ridge Regression:")
    # ridge = Ridge(alpha=10.0)
    # ridge, mae_ridge = date_taken_train_model(train, ridge)
    # test_preds_ridge, metrics_ridge = evaluate(ridge, test)
    """
    alpha| test mae | train mae
    10.0 | 25.40    | 24.92
    02.0 | 25.42    | 24.92
    01.0 | 25.41    | 24.92
    """
    
    # print("degree 2 Polynomial Regression:")
    # poly_model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
    # poly_model, mae_poly = date_taken_train_model(train, poly_model)
    # test_preds_poly, metrics_poly = evaluate(poly_model, test)
    """
    ArrayMemoryError: Unable to allocate 70.0 GiB for an array with shape (63492, 296065) and data type float32
    """

    print("SupportVectorRegression:")
    svr = SVR(kernel="rbf", C=50.0, gamma="scale")
    svr, mae_svr = date_taken_train_model(train, svr)
    joblib.dump(svr, "svr50_siglip320_model.joblib")
    test_preds_svr, metrics_svr = evaluate(svr, test)
    """
        SupportVectorRegression: C=10
    Train  MeanAbsoluteError: 19.61 years
    Test   MeanAbsoluteError: 21.27 years

        SupportVectorRegression: C=50
    Train  MeanAbsoluteError: 15.14 years
    Test   MeanAbsoluteError: 19.95 years

        SupportVectorRegression: C=100
    Train  MeanAbsoluteError: 12.37 years
    Test   MeanAbsoluteError: 19.6 years
    """

    # print("Random Forest:")
    # rf = RandomForestRegressor(n_estimators=300, max_depth=None, random_state=0)
    # rf, mae_rf = date_taken_train_model(train, rf)
    # test_preds_rf, metrics_rf = evaluate(rf, test)
    
    # print("Gradient Boosting:")
    # gbr = GradientBoostingRegressor(random_state=0)
    # gbr, mae_gbr = date_taken_train_model(train, gbr)
    # test_preds_gbr, metrics_gbr = evaluate(gbr, test)

    # Nearest Neighbor