import joblib
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.svm import SVR
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from datetime import datetime
from sqlalchemy import text
from src.trainer.db import photos_with_siglip_enbedding


def date_taken_train_model(train, model):
    """"trains and returns the given models on the given data"""
    X = np.stack(train["sig_lip_vect_n"].values)
    y = train["year"]
    model.fit(X, y)
    y_pred = model.predict(X)
    mae = mean_absolute_error(y, y_pred)
    print(f"Train  MeanAbsoluteError: {round(mae, 2)} years")
    return model, mae

def random_baseline(train):
    """evaluate the performance of a random output"""
    np.random.seed(42)
    random_preds = np.random.randint(1850, 2027, size=len(train))
    mae_random = mean_absolute_error(train["year"], random_preds)
    print(f"Random MeanAbsoluteError: {round(mae_random,2)} years")  # Should be ~44
    return mae_random

def evaluate(model, test):
    """turns embeddings into a prediction using the model"""
    X_test = np.stack(test["sig_lip_vect_n"].values)
    y_test = test["year"]
    y_pred = model.predict(X_test)
    test = test.copy()
    test["prediction"] = y_pred
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Test   MeanAbsoluteError: {round(mae, 2)} years")
    return test, {"mae": mae}

def save_predictions(model, photos):
    """writes predicted dates to the databse"""
    engine = get_db_connection("trainer")
    for idx, row in photos.iterrows():
        try:
            prediction = row['svr_50']
            update_query = text("""
            UPDATE machine_learning_photo 
            SET reg_n_pred_date = :prediction
            WHERE owner_nsid = :owner_nsid AND id = :id
        """)
            with engine.connect() as conn:
                conn.execute(update_query, {
                    'prediction': int(prediction),
                    'owner_nsid': row['owner_nsid'],
                    'id': row['id']
                })
                conn.commit()
            print(f"{idx} : was dated from {prediction}")
        except Exception as e:
            print(f"❌ owner_nsid = '{row['owner_nsid']}' AND id = {row['id']}\n {e}")
            continue


if __name__ == "__main__":
    photos, train, test = photos_with_siglip_enbedding()

    """SVR has been best performing in a reasonable time (see alternatives below)"""
    print("SupportVectorRegression:")
    svr = joblib.load("models/svr50_siglip320_model.joblib")
    if svr:
        preds_svr, metrics_svr = evaluate(svr, photos)
        photos['svr_50'] = preds_svr["prediction"].values
        save_predictions(svr, photos)
    else:
        svr = SVR(kernel="rbf", C=50.0, gamma="scale")
        svr, mae_svr = date_taken_train_model(train, svr)
        joblib.dump(svr, "models/svr50_siglip320_model.joblib")
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

    # print("Random Forest:")
    # rf = RandomForestRegressor(n_estimators=300, max_depth=None, random_state=0)
    # rf, mae_rf = date_taken_train_model(train, rf)
    # test_preds_rf, metrics_rf = evaluate(rf, test)
    
    # print("Gradient Boosting:")
    # gbr = GradientBoostingRegressor(random_state=0)
    # gbr, mae_gbr = date_taken_train_model(train, gbr)
    # test_preds_gbr, metrics_gbr = evaluate(gbr, test)

    # Nearest Neighbor