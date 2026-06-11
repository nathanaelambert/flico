import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import text

from ..core.db import get_engine


def plot_descr_pred_date_histogram():
    sql = """--sql
    SELECT
        descr_pred_date,
        count(*) AS n
    FROM machine_learning_photo
    WHERE descr_pred_date IS NOT NULL
    GROUP BY descr_pred_date
    ORDER BY descr_pred_date
    """

    with get_engine("server").connect() as conn:
        df = pd.read_sql(text(sql), conn)

    years = df["descr_pred_date"].astype(int).to_numpy()
    counts = df["n"].to_numpy()

    fig, ax = plt.subplots(figsize=(14, 6))
    colors = [
        "red" if year % 10 == 0 else "black"
        for year in years
    ]

    ax.bar(
        years,
        counts,
        width=1.0,
        color=colors,
        edgecolor=colors,
        linewidth=0.5,
    )

    xmin = 1600
    xmax = 2026

    ax.set_xlim(xmin-1, xmax+1)
    ax.set_ylim(0, 50000)

    tick_start = (xmin // 25) * 25
    tick_end = ((xmax + 24) // 25) * 25

    ticks = np.arange(tick_start, tick_end + 1, 25)

    ax.set_xticks(ticks)
    ax.set_yticks(np.arange(0, 50001, 10000))
    ax.tick_params(axis="x", rotation=45)

    ax.set_xlabel("Predicted year")
    ax.set_ylabel("Count")
    ax.set_title(f"Distribution of descr_pred_date (n={counts.sum():,})")

    output_file = "exported_plots/descr_pred_date_histogram_new.png"

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

def plot_descr_pred_date_histogram_69():
    sql = """--sql
    SELECT
        descr_pred_date,
        count(*) AS n
    FROM machine_learning_photo
    WHERE descr_pred_date IS NOT NULL
      AND p_descr_date > 0.69
    GROUP BY descr_pred_date
    ORDER BY descr_pred_date
    """

    with get_engine("server").connect() as conn:
        df = pd.read_sql(text(sql), conn)

    years = df["descr_pred_date"].astype(int).to_numpy()
    counts = df["n"].to_numpy()

    fig, ax = plt.subplots(figsize=(14, 6))
    colors = [
        "red" if year % 10 == 0 else "black"
        for year in years
    ]

    ax.bar(
        years,
        counts,
        width=1.0,
        color=colors,
        edgecolor=colors,
        linewidth=0.5,
    )

    xmin = 1600
    xmax = 2026

    ax.set_xlim(xmin-1, xmax+1)
    ax.set_ylim(0, 50000)

    tick_start = (xmin // 25) * 25
    tick_end = ((xmax + 24) // 25) * 25

    ticks = np.arange(tick_start, tick_end + 1, 25)

    ax.set_xticks(ticks)
    ax.set_yticks(np.arange(0, 50001, 10000))
    ax.tick_params(axis="x", rotation=45)

    ax.set_xlabel("Predicted year")
    ax.set_ylabel("Count")
    ax.set_title(f"Distribution of descr_pred_date (n={counts.sum():,})")

    output_file = "exported_plots/descr_pred_date_histogram_new_69.png"

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()


def plot_date_taken_histogram():
    sql = """--sql
    SELECT
        EXTRACT(YEAR FROM date_taken) AS year,
        count(*) AS n
    FROM photo
    WHERE date_taken IS NOT NULL
    GROUP BY year
    ORDER BY year
    """

    with get_engine("server").connect() as conn:
        df = pd.read_sql(text(sql), conn)

    years = df["year"].astype(int).to_numpy()
    counts = df["n"].to_numpy()

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.bar(
        years,
        counts,
        width=1.0,
        color="black",
        edgecolor="black",
        linewidth=0.5,
    )

    xmin = 1600
    xmax = 2026

    ax.set_xlim(xmin - 1, xmax + 1)
    ax.set_ylim(0, 50000)

    ticks = np.arange(
        (xmin // 25) * 25,
        ((xmax + 24) // 25) * 25 + 1,
        25,
    )

    ax.set_xticks(ticks)
    ax.set_yticks(np.arange(0, 50001, 10000))
    ax.tick_params(axis="x", rotation=45)

    ax.set_xlabel("Photo year")
    ax.set_ylabel("Count")
    ax.set_title(f"Distribution of photo.date_taken year (n={counts.sum():,})")

    output_file = "exported_plots/date_taken_histogram_new.png"

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

def plot_date_agreement_histogram():
    sql = """--sql
    SELECT
        mlp.descr_pred_date AS year,
        count(*) AS n
    FROM machine_learning_photo AS mlp
    JOIN photo AS p
        ON p.id = mlp.id
       AND p.owner_nsid = mlp.owner_nsid
    WHERE mlp.descr_pred_date IS NOT NULL
      AND EXTRACT(YEAR FROM p.date_taken) = mlp.descr_pred_date
    GROUP BY mlp.descr_pred_date
    ORDER BY mlp.descr_pred_date
    """

    with get_engine("server").connect() as conn:
        df = pd.read_sql(text(sql), conn)

    years = df["year"].astype(int).to_numpy()
    counts = df["n"].to_numpy()

    fig, ax = plt.subplots(figsize=(14, 6))

    ax.bar(
        years,
        counts,
        width=1.0,
        color="black",
        edgecolor="black",
        linewidth=0.5,
    )

    xmin = 1600
    xmax = 2026

    ax.set_xlim(xmin - 1, xmax + 1)
    ax.set_ylim(0, 50000)

    ticks = np.arange(
        (xmin // 25) * 25,
        ((xmax + 24) // 25) * 25 + 1,
        25,
    )

    ax.set_xticks(ticks)
    ax.set_yticks(np.arange(0, 50001, 10000))
    ax.tick_params(axis="x", rotation=45)

    ax.set_xlabel("Year")
    ax.set_ylabel("Matching photos")
    ax.set_title(f"Agreement: photo year == predicted year (n={counts.sum():,})")

    output_file = "exported_plots/date_agreement_histogram_new.png"

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

def plot_probability_histogram(
    column: str,
    output_file: str,
):
    sql = f"""--sql
    SELECT {column}
    FROM machine_learning_photo
    WHERE {column} IS NOT NULL
    """

    with get_engine("server").connect() as conn:
        df = pd.read_sql(text(sql), conn)

    values = df[column].astype(float).to_numpy()

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.hist(
        values,
        bins=100,
        range=(0, 1),
        density=True,
        color="black",
        edgecolor="black",
        linewidth=0.5,
    )

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ax.set_xticks(np.arange(0, 1.01, 0.1))
    ax.set_yticks(np.arange(0, 1.01, 0.1))

    ax.set_xlabel("Probability")
    ax.set_ylabel("Density")
    ax.set_title(f"Distribution of {column}")

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches="tight")
    plt.close()

if __name__ == "__main__":
    plot_descr_pred_date_histogram()
    plot_descr_pred_date_histogram_69()
    plot_date_taken_histogram()
    plot_date_agreement_histogram()

    plot_probability_histogram(
        "p_descr_date",
        "exported_plots/p_descr_date_histogram_new.png",
    )

    plot_probability_histogram(
        "p_descr_date_1",
        "exported_plots/p_descr_date_1_histogram_new.png",
    )

    plot_probability_histogram(
        "p_descr_date_2",
        "exported_plots/p_descr_date_2_histogram_new.png",
    )
