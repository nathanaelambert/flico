import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, html, Input, Output, callback, ctx, no_update, ALL, State, dash_table, dcc, MATCH

from src.server.db import count_flickr, count_date, count_description, sample_from_flickr

TABLES = {
    "flickr": count_flickr,
    "date": count_date,
    "description": count_description,
    # "geo": count_geo 
}

titles = {
    "flickr": "Downloaded from Flickr",
    "date": "With valid date",
    "description" : "With valid description",
    # "geo": "With valid geo data"
}

app = Dash(__name__)

tables_layout = []
for key in TABLES:
    tables_layout.extend([
        html.H3(titles[key], style={'align-self': 'center'}),
        dcc.Loading(
            id={"type": "loading-table", "index": key},
            type="dot",
            children=dash_table.DataTable(
                id={"type": "table", "index": key},
                data=[],
                columns=[{"name": i, "id": i} for i in ["institution", "pictures"]],
                style_cell_conditional=[
                    {'if': {'column_id': 'institution'}, 'textAlign': 'left'},
                    {'if': {'column_id': 'pictures'}, 'textAlign': 'right'}
                ]
            )
        )
    ])

app.layout = html.Div(
    tables_layout,
    style={
        'display': 'flex', 
        'flexDirection': 'column', 
        'padding': '20px', 
        'maxWidth': '740px',
        'margin': '0 auto'
    }
)
@callback(
    Output({"type": "table", "index": MATCH}, "data"),
    Output({"type": "table", "index": MATCH}, "columns"),
    Input({"type": "table", "index": MATCH}, "id")
)
def load_table(table_id):
    key = table_id["index"]
    if key not in TABLES:
        raise dash.exceptions.PreventUpdate
    df = TABLES[key]()
    return (
        df.to_dict("records"),
        [{"name": i, "id": i} for i in df.columns]
    )

if __name__ == "__main__":
    app.run(debug=False)