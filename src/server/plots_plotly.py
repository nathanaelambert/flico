import seaborn as sns
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

EXPORT_FOLDER = "../../exported_plots/"

def plot_institutions_per_year(df):
    """expects columns 'date_taken', 'owner_name"""
    df['year'] = pd.to_datetime(df['date_taken'], errors='coerce').dt.year
    return _plot_stacked(df, 'Pictures by Year by Institutions')

def plot_institutions_per_predicted_year(df):
    """expects columns 'reg_n_pred_date', 'owner_name'"""
    df['year'] = df['reg_n_pred_date']
    return _plot_stacked(df, 'Pictures by Predicted Year by Institutions')

def plot_confusion_between_prediction_and_true_value(df, display=True, column='reg_n_pred_date'):
    """expects columns 'date_taken', 'reg_n_pred_date', 'owner_name', 'url_n'"""    
    pivot_df = df.groupby(['true_date', 'owner_name']).size().reset_index(name='count')
    owner_order = pivot_df.groupby('owner_name')['count'].sum().sort_values(ascending=False).index.tolist()
    
    fig = px.scatter(
        df,
        x='true_date',
        y=column,
        color='owner_name',
        labels={'x': 'Year', 'y': f"Predicted Year ({column})"},
        custom_data=['owner_name', 'url_n', 'page_url'],
        category_orders={'owner_name': owner_order},
        color_discrete_sequence=px.colors.qualitative.Pastel1 + px.colors.qualitative.Pastel2
    )
    for trace in fig.data:
        trace.update(
            mode='markers',
            marker=dict(size=3, opacity=0.9),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>" +
                "True: %{x}<br>" +
                "Pred: %{y}<br>" +
                "Image: %{customdata[1]}<extra></extra>"
            ),
        )
    fig.update_layout(
        width=1100,
        height=800,
        margin=dict(l=50, r=50, t=60, b=50),
        legend=dict(entrywidth=100),
        legend_title='Owner Name',
        xaxis_tickangle=45,
        plot_bgcolor='white',  
        hovermode='closest',
        clickmode='event+select'
    )
    x_ticks = list(range(df['true_date'].min() // 10 * 10, df['true_date'].max() // 10 * 10 + 20, 10))
    y_ticks = list(range(df[column].min() // 10 * 10, df[column].max() // 10 * 10 + 20, 10))
    fig.update_xaxes(
        range=[1800, 2050],
        gridcolor='lightgray',
        tickmode='array',
        tickvals=x_ticks,
    )
    fig.update_yaxes(
        range=[1800, 2050],
        gridcolor='lightgray',
        tickmode='array',
        tickvals=y_ticks,
    ) 
    _add_x_equal_y_line(fig)
    _add_calibration_lines(fig, df, column)
    if display:
        fig.show()
    # fig.write_html(EXPORT_FOLDER + "plot_confusion_between_prediction_and_true_value.html")
    return fig

def _add_x_equal_y_line(fig):
    fig.add_shape(
        type="line",
        x0=1800, y0=1800,
        x1=2050, y1=2050,
        line=dict(color="grey", width=1, dash="dash")
    )

def _add_calibration_lines(fig, df, column):
    agg = (
        df.groupby("true_date")[column]
        .agg(["mean", "std", "count"])
        .reset_index()
    )
    agg = agg.rename(
        columns={
            "true_date": "true_year",
            "mean": "pred_mean",
            "std": "pred_std",
            "count": "n",
        }
    )
    agg["pred_std"] = agg["pred_std"].fillna(0)
    agg = agg.dropna(subset=["true_year", "pred_mean"])
    agg["pred_upper"] = agg["pred_mean"] + agg["pred_std"]
    agg["pred_lower"] = agg["pred_mean"] - agg["pred_std"]
    agg = agg.sort_values("true_year")
    fig.add_trace(
        go.Scattergl(
            x=agg["true_year"],
            y=agg["pred_mean"],
            mode="lines",
            line=dict(color="black", width=2),
            name="mean predicted_year",
            showlegend=True,
        )
    )
    fig.add_trace(
        go.Scattergl(
            x=agg["true_year"],
            y=agg["pred_upper"],
            mode="lines",
            line=dict(color="black", width=2, dash="dot"),
            name="mean + std",
            showlegend=True,
        )
    )
    fig.add_trace(
        go.Scattergl(
            x=agg["true_year"],
            y=agg["pred_lower"],
            mode="lines",
            line=dict(color="black", width=2, dash="dot"),
            name="mean - std",
            showlegend=True,
        )
    )

    
def _plot_stacked(df, plot_title, log_scale=False):      
    pivot_df = df.groupby(['year', 'owner_name']).size().reset_index(name='count')
    owner_totals = pivot_df.groupby('owner_name')['count'].sum().sort_values(ascending=False)
    owner_order = owner_totals.index.tolist()
    
    fig = px.bar(
        pivot_df, 
        x='year', 
        y='count', 
        color='owner_name',
        title=plot_title,
        barmode='stack',
        category_orders={'owner_name': owner_order},
        color_discrete_sequence=px.colors.qualitative.Light24 + px.colors.qualitative.Dark24 + 
                               px.colors.qualitative.Set3 + px.colors.qualitative.Pastel1 + 
                               px.colors.qualitative.Pastel2
    )
    
    fig.update_layout(
        xaxis_title='Year',
        yaxis_title='Count' + (' (Log Scale)' if log_scale else ''),
        legend_title='Owner Name',
        xaxis_tickangle=45,
        plot_bgcolor='white',  
    )
    fig.update_xaxes(
        tickmode='linear',
        tick0=df['year'].min() // 10 * 10,
        dtick=10,
    )
    fig.update_yaxes(
        gridcolor='lightgray' 
    ) 
    if log_scale:
        fig.update_layout(yaxis_type='log')
    
    fig.show()
    return fig


def plot_join_preds_actual_dates(df):
    sns.set_theme(style="darkgrid")
    df = df.copy()
    df['true_date'] = pd.to_datetime(df['date_taken'], errors='coerce').dt.year
    x = df['true_date']
    y = df['reg_n_pred_date']
    g = sns.jointplot(
        x=x,
        y=y,
        kind="reg",
        marginal_kws={"bins": 180, "fill": True},
        marginal_ticks=True,
        height=7,
        ratio=5,
        space=0.2,
        color="m"
    )
    g.ax_joint.set_xlim(1800, 2050)
    g.ax_joint.set_ylim(1800, 2050)
    lims = (1800, 2050)
    g.ax_joint.plot(lims, lims, "k--", alpha=0.7, linewidth=1.5)
    g.set_axis_labels("actual_year", "predicted_year")
    return g