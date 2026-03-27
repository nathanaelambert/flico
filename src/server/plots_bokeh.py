from bokeh.io import curdoc, output_notebook
from bokeh.plotting import figure, show
from bokeh.models import ColumnDataSource, HoverTool, CustomJS
import pandas as pd
import numpy as np

from src.server.db import photos

curdoc().theme = "dark_minimal"

df = photos()

date_range = [1800, 2050]
cell_dim = 10
source = ColumnDataSource(df)

p = figure(
    title="320px + SigLip + SVR", 
    x_axis_label="True Date", 
    y_axis_label="Predicted Date",
    width=800,
    height=800,
    tools='pan,wheel_zoom,box_zoom,reset,save,tap',
)

scatter = p.scatter(
    'true_date', 
    'reg_n_pred_date', 
    source=source,
    legend_label="Picture", 
    size=16)
callback = CustomJS(args=dict(source=source), code="""
    const indices = cb_data.index.indices;
    if (indices.length > 0) {
        alert('hey');
    }
""")
scatter.js_on_event('tap', callback)
show(p)