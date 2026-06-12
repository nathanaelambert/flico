from ..core.db import get_photos_where

import numpy as np
import pandas as pd


def mae(df, pred_col, target_col="human_pred_date"):
    valid = df[[pred_col, target_col]].dropna()

    if len(valid) == 0:
        return np.nan

    return np.abs(valid[pred_col] - valid[target_col]).mean()


def evaluate_periods(sample_size=100):
    periods = [
        ("<1800", None, 1800),
        ("1800-1849", 1800, 1850),
        ("1850-1899", 1850, 1900),
        ("1900-1949", 1900, 1950),
        ("1950-1999", 1950, 2000),
        (">2000", 2000, None),
    ]

    results = []

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

        results.append({
            "period": label,
            "n": len(df),
            "visual predictor": mae(df, "reg_n_pred_date"),
            "best textual candidate": mae(df, "descr_pred_date"),
            "year taken metadata": mae(df, "year_taken"),
            "aggregated year": mae(df, "corrected_year"),
        })

    results = pd.DataFrame(results)

    print(results.to_string(index=False))
    return results

if __name__ == "__main__":
    evaluate_periods()


"""
MeanAverageError per period per model

period   n  visual predictor  best textual candidate  year taken metadata  aggregated year
    <1800 100        233.191919                3.282828               265.48             0.02
1800-1849 100         80.489583                0.020000                97.73             0.09
1850-1899 100         34.938144               23.700000                71.04             1.15
1900-1949 100         15.200000               49.847826                42.54             0.15
1950-1999 100         14.780000               11.804124                27.95             0.46
    >2000 100          8.370000               12.731707                 0.47             0.13

"""