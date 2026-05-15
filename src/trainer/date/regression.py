import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.svm import SVR
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from datetime import datetime
from huggingface_hub import hf_hub_download
import src.utils.colors as c

print(f"Loading HuggingFace model for SVR50 regression...{c.GREY}")
model_path = hf_hub_download(
    repo_id="nathanaelambert/svr50siglip320flico-05-2026",
    filename="svr50_siglip320_model.joblib"
)
svr_model = joblib.load(model_path)
print(f"Model loaded successfully!{c.RESET}")

def svr50_predictions(df: pd.DataFrame)-> pd.DataFrame:
    """ predicts dates from siglip embedding using SVR trained model"""
    X = np.stack(df['sig_lip_vect_n'].values)
    preds = svr_model.predict(X)
    df = df.copy()
    df['reg_n_pred_date'] = preds
    print(f"Predicted dates for {len(df)} pictures.")
    return df

def train_model(train: pd.DataFrame, test: pd.DataFrame):
    ## NOT TESTED
    """trains and evaluate a regression model given the provided data"""
    svr = SVR(kernel="rbf", C=50.0, gamma="scale")
    svr, mae_svr = _date_taken_train_model(train, svr)
    joblib.dump(svr, "models/svr50_siglip320_model.joblib")
    test_preds_svr, metrics_svr = _evaluate(svr, test)

def _date_taken_train_model(train, model):
    """"trains and returns the given models on the given data"""
    X = np.stack(train["sig_lip_vect_n"].values)
    y = train["year"]
    model.fit(X, y)
    y_pred = model.predict(X)
    mae = mean_absolute_error(y, y_pred)
    print(f"Train  MeanAbsoluteError: {round(mae, 2)} years")
    return model, mae

def _random_baseline(train):
    """evaluate the performance of a random output"""
    np.random.seed(42)
    random_preds = np.random.randint(1850, 2027, size=len(train))
    mae_random = mean_absolute_error(train["year"], random_preds)
    print(f"Random MeanAbsoluteError: {round(mae_random,2)} years")
    return mae_random

def _evaluate(model, test):
    """turns embeddings into a prediction using the model"""
    X_test = np.stack(test["sig_lip_vect_n"].values)
    y_test = test["year"]
    y_pred = model.predict(X_test)
    test = test.copy()
    test["prediction"] = y_pred
    mae = mean_absolute_error(y_test, y_pred)
    print(f"Test   MeanAbsoluteError: {round(mae, 2)} years")
    return test, {"mae": mae}
   
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
# mae_random = _random_baseline(train)
"""baseline random
Random MeanAbsoluteError: 57.59 years
"""

# print("Linear Regression:")
# model_lin, mae_lin = _date_taken_train_model(train, LinearRegression())
# test_preds_lin, metrics_lin = _evaluate(model_lin, test)
""" RESULTS (march 20 2026):
Train  MeanAbsoluteError: 24.98 years
Test   MeanAbsoluteError: 25.45 years
"""

# print("Ridge Regression:")
# ridge = Ridge(alpha=10.0)
# ridge, mae_ridge = _date_taken_train_model(train, ridge)
# test_preds_ridge, metrics_ridge = _evaluate(ridge, test)
"""
alpha| test mae | train mae
10.0 | 25.40    | 24.92
02.0 | 25.42    | 24.92
01.0 | 25.41    | 24.92
"""

# print("degree 2 Polynomial Regression:")
# poly_model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
# poly_model, mae_poly = _date_taken_train_model(train, poly_model)
# test_preds_poly, metrics_poly = _evaluate(poly_model, test)
"""
ArrayMemoryError: Unable to allocate 70.0 GiB for an array with shape (63492, 296065) and data type float32
"""

# print("Random Forest:")
# rf = RandomForestRegressor(n_estimators=300, max_depth=None, random_state=0)
# rf, mae_rf = _date_taken_train_model(train, rf)
# test_preds_rf, metrics_rf = _evaluate(rf, test)

# print("Gradient Boosting:")
# gbr = GradientBoostingRegressor(random_state=0)
# gbr, mae_gbr = _date_taken_train_model(train, gbr)
# test_preds_gbr, metrics_gbr = _evaluate(gbr, test)

# Nearest Neighbor