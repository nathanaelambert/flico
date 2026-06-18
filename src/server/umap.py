from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import text
from sklearn.preprocessing import normalize
import umap
from matplotlib.colors import Normalize

from ..core.db import get_engine


query = text("""
    SELECT sig_lip_vect_n, corrected_year
    FROM machine_learning_photo
    WHERE corrected_year IS NOT NULL
    AND sig_lip_vect_n is not NULL
    ORDER BY RANDOM()
    LIMIT 100000
""")

df = pd.read_sql_query(query, get_engine("server"))
df = df.loc[:, ~df.columns.duplicated()]

for i, x in enumerate(df["sig_lip_vect_n"]):
    arr = np.asarray(x)

    if arr.shape != (768,):
        print(i, arr.shape, type(x))
        break

# Convert embeddings to matrix
X = np.vstack(df["sig_lip_vect_n"].values)

# SigLIP similarity is typically cosine similarity,
# so normalize before projection.
X = normalize(X)

print("Running UMAP...")
reducer = umap.UMAP(
    n_components=2,
    metric="cosine",
    n_neighbors=30,
    min_dist=0.1,
    random_state=42,
)

embedding_2d = reducer.fit_transform(X)

plot_df = pd.DataFrame(
    {
        "x": embedding_2d[:, 0],
        "y": embedding_2d[:, 1],
        "year": df["corrected_year"].values,
    }
)

Path("exported_plots").mkdir(exist_ok=True)

plt.figure(figsize=(12, 10))

sc = plt.scatter(
    plot_df["x"],
    plot_df["y"],
    c=plot_df["year"],
    cmap="viridis",
    norm=Normalize(vmin=1800, vmax=2000),
    s=3,
    alpha=0.7,
)

cbar = plt.colorbar(sc)
cbar.set_label("Year")

plt.title("SigLIP Embeddings projected with UMAP (cosine metric)")
plt.xlabel("UMAP-1")
plt.ylabel("UMAP-2")
plt.tight_layout()

output_path = "exported_plots/siglip_umap_by_year.png"
plt.savefig(output_path, dpi=300)
plt.close()

print(f"Saved: {output_path}")