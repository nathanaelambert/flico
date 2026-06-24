from dash import Dash, html, dcc, Input, Output, State, callback
import pandas as pd

from ...core.db import get_photos_where
from ..db import update_ml_photo


def sample_data():
    df = get_photos_where("server", clause="""--sql
        WHERE corrected_year IS NOT NULL
          AND corrected_year >= 1000
          AND corrected_year <  2000
          AND EXTRACT(YEAR from date_taken) < 2000
          AND EXTRACT(YEAR from date_taken) != descr_pred_date
        ORDER BY RANDOM()
        LIMIT 100
    """)

    df["page"] = (
        "https://www.flickr.com/photos/"
        + df["owner_nsid"]
        + "/"
        + df["id"].astype(str)
    )

    df["year"] = pd.to_datetime(
        df["date_taken"],
        errors="coerce"
    ).dt.year

    return df


df = sample_data()

app = Dash(__name__)

app.layout = html.Div(
    [
        dcc.Store(
            id="rows",
            data=df.to_dict("records")
        ),

        dcc.Store(
            id="current-index",
            data=0
        ),

        # LEFT PANEL
        html.Div(
            [
                html.A(
                    "Open Flickr page",
                    id="page-link",
                    href="",
                    target="_blank",
                    style={
                        "fontSize": "20px",
                        "fontWeight": "bold",
                    }
                ),

                html.Br(),
                html.Br(),

                html.Div(
                    id="owner-name",
                    style={
                        "fontSize": "18px",
                        "fontWeight": "bold",
                    }
                ),

                html.H2(id="title"),

                html.Img(
                    id="photo",
                    style={
                        "width": "100%",
                        "maxHeight": "80vh",
                        "objectFit": "contain",
                        "border": "1px solid #ddd",
                    }
                ),

                html.Hr(),

                html.H4("Description"),

                html.Div(
                    id="description",
                    style={
                        "whiteSpace": "pre-wrap",
                        "maxHeight": "300px",
                        "overflowY": "auto",
                        "border": "1px solid #ddd",
                        "padding": "10px",
                    }
                ),

                html.Hr(),

                html.H4("Tags"),

                html.Div(
                    id="tags",
                    style={
                        "whiteSpace": "pre-wrap",
                        "fontSize": "14px",
                    }
                ),
            ],
            style={
                "width": "75%",
                "display": "inline-block",
                "verticalAlign": "top",
                "padding": "15px",
                "boxSizing": "border-box",
            }
        ),

        # RIGHT PANEL
        html.Div(
            [
                html.H3(id="progress"),

                html.Hr(),

                html.Pre(
                    id="metadata",
                    style={
                        "fontSize": "16px",
                        "whiteSpace": "pre-wrap",
                    }
                ),

                html.Hr(),

                html.Label(
                    "Annotated date",
                    style={"fontWeight": "bold"}
                ),

                dcc.Input(
                    id="annotation",
                    type="text",
                    maxLength=4,
                    autoFocus=True,
                    placeholder="YYYY",
                    style={
                        "fontSize": "28px",
                        "width": "140px",
                    }
                ),

                html.Div(
                    id="error",
                    style={
                        "color": "red",
                        "marginTop": "10px",
                    }
                ),

                html.Br(),

                html.Div(
                    [
                        html.P("Press Enter to submit."),
                        html.P("Empty input + Enter = skip."),
                    ]
                ),
            ],
            style={
                "width": "24%",
                "display": "inline-block",
                "verticalAlign": "top",
                "padding": "15px",
                "boxSizing": "border-box",
                "position": "sticky",
                "top": "0",
            }
        ),
    ]
)


@callback(
    Output("photo", "src"),
    Output("title", "children"),
    Output("owner-name", "children"),
    Output("description", "children"),
    Output("tags", "children"),
    Output("page-link", "href"),
    Output("progress", "children"),
    Output("metadata", "children"),
    Input("current-index", "data"),
    State("rows", "data"),
)
def display_row(idx, rows):

    if idx >= len(rows):
        return (
            "",
            "DONE",
            "",
            "",
            "",
            "",
            f"{len(rows)}/{len(rows)}",
            "No more photos."
        )

    row = rows[idx]

    metadata = "\n".join([
        f"visual       : {row.get('reg_n_pred_date')}",
        f"qwen3        : {row.get('qwen3_pred_date')}",
        f"date_taken   : {row.get('year')}",
        f"combined year: {row.get('corrected_year')}",
        "",
        f"textual 1: {(row.get('descr_pred_date')   or ''):>4}  p={(row.get('p_descr_date')   or 0):.3f}",
        f"textual 2: {(row.get('descr_pred_date_1') or ''):>4}  p={(row.get('p_descr_date_1') or 0):.3f}",
        f"textual 3: {(row.get('descr_pred_date_2') or ''):>4}  p={(row.get('p_descr_date_2') or 0):.3f}",
    ])

    return (
        row.get("url_n", ""),
        row.get("title", ""),
        row.get("owner_name", ""),
        row.get("description", ""),
        row.get("tags", ""),
        row["page"],
        f"{idx + 1}/{len(rows)}",
        metadata,
    )


@callback(
    Output("current-index", "data"),
    Output("annotation", "value"),
    Output("error", "children"),
    Input("annotation", "n_submit"),
    State("annotation", "value"),
    State("current-index", "data"),
    State("rows", "data"),
    prevent_initial_call=True,
)
def submit_annotation(_, value, idx, rows):

    if idx >= len(rows):
        return idx, "", ""

    value = (value or "").strip()

    #
    # Empty input => skip
    #
    if value == "":
        return idx + 1, "", ""

    #
    # Validate year
    #
    if value != "-1":
        if not (value.isdigit() and len(value) == 4):
            return idx, value, "Please enter exactly 4 digits."

    row = rows[idx]

    update_df = pd.DataFrame([
        {
            "owner_nsid": row["owner_nsid"],
            "id": row["id"],
            "human_pred_date": int(value),
        }
    ])

    update_ml_photo(update_df, "human_pred_date")

    return idx + 1, "", ""


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=8050,
        debug=False,
    )

