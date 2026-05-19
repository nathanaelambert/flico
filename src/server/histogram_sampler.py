import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, callback

from src.server.db import (
    photos,
    benchmark_photos,
    new_granularity_photos,
    description_photos,
)

evaluation = 4

# Load and set index
if evaluation == 1:
    df = photos()
    df = df.set_index(['true_date', 'reg_n_pred_date']).sort_index()
elif evaluation == 2:
    df = benchmark_photos()
    df = df.set_index(['true_date', 'qwen3_pred_date']).sort_index()
elif evaluation == 3:
    df = new_granularity_photos()
    df = df.set_index(['true_date', 'true_date']).sort_index()
elif evaluation == 4:
    df = description_photos()
    df = df[df['descr_pred_date'].notnull()]
    df['descr_pred_date'] = df['descr_pred_date'].astype(int)
    print(f"comparing {len(df)} pictures (description vs metadata)")
    df = df.set_index(['true_date', 'descr_pred_date']).sort_index()

# Axis range and bin width
MIN_YEAR, MAX_YEAR = 1800, 2025
BIN_WIDTH = 5  # 5‑year bins
NBINS = (MAX_YEAR - MIN_YEAR) // BIN_WIDTH  # 45

app = Dash(__name__)
app.layout = html.Div(
    [
        dcc.Graph(id="year-histogram", style={'flex': 1}),
        html.Div(
            id="image_grid",
            style={
                'flex': 1,
                'display': 'flex',
                'flexDirection': 'row',
                'flexWrap': 'wrap',
            },
        ),
    ],
    style={'display': 'flex', 'flexDirection': 'row'},
)


def round_to_bin(x):
    """Round to nearest 5‑year bin center."""
    return BIN_WIDTH * round(x / BIN_WIDTH)


@callback(
    Output("year-histogram", "figure"),
    Input("year-histogram", "relayoutData"),
)
def update_histogram(relayoutData):
    # Filter to 1800–2025 for plotting
    df_plot = df.loc[
        (slice(MIN_YEAR, MAX_YEAR), slice(MIN_YEAR, MAX_YEAR)),
    ].copy()
    x_vals = df_plot.index.get_level_values(0)
    y_vals = df_plot.index.get_level_values(1)

    fig = px.density_heatmap(
        x=x_vals,
        y=y_vals,
        nbinsx=NBINS,
        nbinsy=NBINS,
        histfunc='count',
        labels={'x': 'Label Year', 'y': 'Predicted Year', 'color': 'Count'},
        color_continuous_scale='Viridis',
    )

    # Enforce 5‑year bins and 1800–2025 range
    fig.update_traces(
        xbins=dict(start=MIN_YEAR, end=MAX_YEAR, size=BIN_WIDTH),
        ybins=dict(start=MIN_YEAR, end=MAX_YEAR, size=BIN_WIDTH),
    )
    fig.update_layout(
        xaxis=dict(range=[MIN_YEAR, MAX_YEAR]),
        yaxis=dict(range=[MIN_YEAR, MAX_YEAR]),
        clickmode='event+select',
        xaxis_title="Label Year",
        yaxis_title="Predicted Year",
        height=500,
        width=500,
        coloraxis={
            'cmin': 0,
            'cmid': 1,
            'cmax': 200,
            'showscale': False,
        },
    )
    return fig


@callback(
    Output("image_grid", "children"),
    Input("year-histogram", "clickData"),
    prevent_initial_call=True,
)
def sample(clickData):
    if not clickData:
        return []

    points = clickData["points"][0]
    true_click = points["x"]
    pred_click = points["y"]

    # Round to nearest 5‑year bin
    true_bin = round_to_bin(true_click)
    pred_bin = round_to_bin(pred_click)

    # Force values into 1800–2025 and clamp to int
    true_bin = max(MIN_YEAR, min(MAX_YEAR, true_bin))
    pred_bin = max(MIN_YEAR, min(MAX_YEAR, pred_bin))

    # Bin range: [bin - 2.5, bin + 2.5)
    true_low, true_high = true_bin - 2.5, true_bin + 2.5
    pred_low, pred_high = pred_bin - 2.5, pred_bin + 2.5

    # Convert index to columns for easy filtering
    df_reset = df.reset_index()

    mask = (
        (df_reset['true_date'] >= true_low)
        & (df_reset['true_date'] < true_high)
        & (df_reset['descr_pred_date'] >= pred_low)
        & (df_reset['descr_pred_date'] < pred_high)
        & (df_reset['true_date'] >= MIN_YEAR)
        & (df_reset['true_date'] <= MAX_YEAR)
        & (df_reset['descr_pred_date'] >= MIN_YEAR)
        & (df_reset['descr_pred_date'] <= MAX_YEAR)
    )
    subset = df_reset[mask]

    if subset.empty:
        return [html.P(f"No images in bin: Label={true_bin}, Predicted={pred_bin}.")]

    row = subset.sample(n=1).iloc[0]

    title = row.get('title', 'No title')
    institution = row.get('owner_name', 'no institution')
    true_date = row.get('true_date', true_bin)
    pred_date = row.get('reg_n_pred_date', pred_bin)  # or from your model
    qwen_date = row.get('qwen3_pred_date', 'no qwen date')
    desc_date = row.get('descr_pred_date', 'no desc date')

    image_card = html.Div(
        [
            html.A(f"{title}", href=row.get('page_url', '')),
            html.P(f"Date label  (metadata): {true_date}"),
            html.P(f"Predicted (siglip+svr): {pred_date}"),
            html.P(f"Extracted from descrip: {desc_date}"),
            html.P(f"Baseline       (Qwen3): {qwen_date}"),
            html.P(f"From: {institution}"),
            html.Img(
                src=row.get('url_n', ''),
                style={'width': '100%', 'height': 'auto'}
            ),
        ],
        style={
            'padding': 10,
            'flex': 1,
            'border': '1px solid #ccc',
            'margin': '5px',
        },
    )

    return [image_card]


if __name__ == "__main__":
    app.run(debug=False)