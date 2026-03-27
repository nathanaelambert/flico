import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback, callback_context
from src.server.db import photos

df = photos()

app = Dash(__name__)
app.layout = html.Div([
    dcc.Graph(id="year-histogram", style={'flex': 1}),
    html.Div(id="image_grid", style={'flex': 1, 'display': 'flex', 'flexDirection': 'row', 'flexWrap': 'wrap'}),
], style={'display': 'flex', 'flexDirection': 'row'})

df = df.set_index(['true_date', 'reg_n_pred_date']).sort_index()

@callback(
    Output("year-histogram", "figure"),
    Input("year-histogram", "relayoutData")
)
def update_histogram(relayoutData):
    fig = px.density_heatmap(
        x=df.index.get_level_values(0),  # true_date
        y=df.index.get_level_values(1),  # reg_n_pred_date
        nbinsx=100, nbinsy=100,
        histfunc='count',
        labels={'x': 'True Year', 'y': 'Predicted Year', 'color': 'Count'},
        color_continuous_scale='Viridis',
    )
    fig.update_layout(
        clickmode='event+select',
        xaxis_title="True Year",
        yaxis_title="Predicted Year",
        height=500,
        width=500,
        coloraxis={
            'cmin': 0,
            'cmid':1, 
            'cmax': 100,
            'showscale': False,
        }
    )
    return fig

@callback(
    Output("image_grid", "children"),
    Input("year-histogram", "clickData"),
    prevent_initial_call=True
)
def sample(clickData):
    if not clickData:
        return []
    
    # Use clicked bin coordinates
    points = clickData['points'][0]
    true_year = int(points['x'])
    pred_year = int(points['y'])
    
    try:
        subset = df.loc[(true_year, pred_year)]
        if subset.empty:
            return [html.P(f"No images found for True: {true_year}, Predicted: {pred_year}.")]
        
        row = subset.sample(n=1).iloc[0]
        title = row.get('title', 'No title')
        institution = row.get('owner_name', 'no institution')
        true_date = row.get('true_date', true_year)
        pred_date = row.get('reg_n_pred_date', pred_year)
        
        image_card = html.Div([
            html.A(f"{title}", href=row.get('page_url', '')),
            html.P(f"True: {true_date}. Predicted: {pred_date}. -- From: {institution}"),
            html.Img(src=row.get('url_n', ''), style={'width': '100%', 'height': 'auto'})
        ], style={'padding': 10, 'flex': 1, 'border': '1px solid #ccc', 'margin': '5px'})
        
        return [image_card]
    except KeyError:
        return [html.P(f"No images found for True: {true_year}, Predicted: {pred_year}.")]

if __name__ == "__main__":
    app.run(debug=False)