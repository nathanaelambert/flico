from ..core.db import get_photos_where

import numpy as np
import pandas as pd


def metrics(df, pred_col, target_col="human_pred_date"):
    valid = df[[pred_col, target_col]].dropna()

    if len(valid) == 0:
        return {
            "count": 0,
            "mae": np.nan,
            "median_ae": np.nan,
            "p90_ae": np.nan,
            "mean_error": np.nan,
            "median_error": np.nan,
        }

    error = valid[pred_col] - valid[target_col]
    abs_error = np.abs(error)

    return {
        "count": len(valid),
        "mae": abs_error.mean(),
        "median_ae": abs_error.median(),
        "p90_ae": np.percentile(abs_error, 90),
        "mean_error": error.mean(),
        "median_error": error.median(),
    }


def evaluate_periods(sample_size=100):
    periods = [
        ("<1800", None, 1800),
        ("1800-1849", 1800, 1850),
        ("1850-1899", 1850, 1900),
        ("1900-1949", 1900, 1950),
        ("1950-1999", 1950, 2000),
        (">=2000", 2000, None),
    ]

    models = {
        "Visual": "reg_n_pred_date",
        "Text": "descr_pred_date",
        "Metadata": "year_taken",
        "Aggregated": "corrected_year",
    }

    rows = []

    for label, low, high in periods:
        where = """
            human_pred_date IS NOT NULL
            AND human_pred_date > 0
        """

        if low is not None:
            where += f"\nAND human_pred_date >= {low}"

        if high is not None:
            where += f"\nAND human_pred_date < {high}"

        df = get_photos_where(
            "server",
            clause=f"""--sql
                WHERE {where}
                ORDER BY RANDOM()
                LIMIT {sample_size}
            """
        )

        if df.empty:
            continue

        df["year_taken"] = pd.to_datetime(
            df["date_taken"],
            errors="coerce"
        ).dt.year

        for model_name, col in models.items():
            m = metrics(df, col)

            rows.append({
                "period": label,
                "model": model_name,
                **m,
            })

    results = pd.DataFrame(rows)

    metric_names = {
        "mae": "MAE",
        "median_ae": "Median Absolute Error",
        "p90_ae": "90th Percentile Absolute Error",
        "mean_error": "Mean Error (Bias)",
        "median_error": "Median Error (Bias)",
        "count": "Coverage",
    }

    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)

    for metric_key, metric_title in metric_names.items():
        print("\n")
        print("=" * 100)
        print(metric_title.upper())
        print("=" * 100)

        table = results.pivot(
            index="period",
            columns="model",
            values=metric_key,
        )

        if metric_key != "count":
            table = table.round(2)

        print(table.to_string())

    return results


if __name__ == "__main__":
    evaluate_periods(sample_size=100)


"""


====================================================================================================
MAE
====================================================================================================
model      Aggregated  Metadata   Text  Visual
period                                        
1800-1849        0.08     87.45   0.01   82.=
1850-1899        1.07     70.38  14.88   32.98
1900-1949        1.25     46.23  23.35   15.41
1950-1999        0.44     26.60  25.07   16.35
<1800            0.21    259.23   1.77  230.96
>=2000           5.13      5.46   6.25   13.78


====================================================================================================
MEDIAN ABSOLUTE ERROR
====================================================================================================
model      Aggregated  Metadata  Text  Visual
period                                       
1800-1849         0.0      22.0   0.0    75.0
1850-1899         0.0      73.0   0.0    29.0
1900-1949         0.0      79.5   0.0    11.0
1950-1999         0.0      23.0   0.0     9.5
<1800             0.0     268.5   0.0   199.0
>=2000            0.0       0.0   0.0     5.0


====================================================================================================
90TH PERCENTILE ABSOLUTE ERROR
====================================================================================================
model      Aggregated  Metadata  Text  Visual
period                                       
1800-1849         0.0     200.2   0.0   162.6
1850-1899         0.0     140.0   0.0    61.4
1900-1949         0.0      99.2   0.0    32.2
1950-1999         0.0      57.2   2.5    39.0
<1800             0.0     372.0   0.0   327.6
>=2000            0.0       0.1   0.0    16.2


====================================================================================================
MEAN ERROR (BIAS)
====================================================================================================
model      Aggregated  Metadata   Text  Visual
period                                        
1800-1849        0.00     87.45   0.01   82.95
1850-1899        0.97     54.34 -12.88   30.65
1900-1949        1.01      4.67 -20.63    3.43
1950-1999       -0.40     20.32 -25.07   -8.27
<1800            0.19    259.23   1.53  230.96
>=2000          -5.11     -4.58  -6.23  -12.00


====================================================================================================
MEDIAN ERROR (BIAS)
====================================================================================================
model      Aggregated  Metadata  Text  Visual
period                                       
1800-1849         0.0      22.0   0.0    75.0
1850-1899         0.0       0.0   0.0    29.0
1900-1949         0.0       0.0   0.0     4.0
1950-1999         0.0      18.0   0.0    -1.5
<1800             0.0     268.5   0.0   199.0
>=2000            0.0       0.0   0.0    -4.0


====================================================================================================
COVERAGE
====================================================================================================
model      Aggregated  Metadata  Text  Visual
period                                       
1800-1849         100       100   100      95
1850-1899         100       100   100      97
1900-1949         100       100    91     100
1950-1999         100       100    96     100
<1800             100       100   100      99
>=2000            100       100    84     100
"""