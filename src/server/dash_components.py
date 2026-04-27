import random
from dash import html, Dash, Input, Output, callback, ctx, MATCH, ALL, no_update, State
import random
from dash import html

class Row:
    def __init__(self, field_name, value):
        self.left = field_name
        self.right = value
    
    def render(self, n_clicks=None):
        return html.Div(
            children=[

            ],
            style={

            }
        )
        
class Block:
    def __init__(self, title, count):
        self.title = title
        self.count = count
        self.id = f"block-{title.lower().replace(' ', '-')}"
        self.items = [Item(i+1) for i in range(count)]  # Store items
    
    def render(self):
        items = [item.render() for item in self.items]
        
        return html.Div(
            id=self.id,
            style={
                'width': '340px',
                'margin': '10px',
                'borderRadius': '10px',
                'border': '2px solid #ccc',
                'display': 'flex',
                'flexDirection': 'column',
                'alignItems': 'center',
                'padding': '15px',
                'boxShadow': '0 4px 8px rgba(0,0,0,0.1)',
                'backgroundColor': 'white'
            },
            children=[
                html.H2(
                    self.title,
                    style={
                        'margin': '0 0 15px 0',
                        'textAlign': 'center',
                        'color': '#333',
                        'fontSize': '20px'
                    }
                ),
                html.Div(id=f"{self.id}-items-container", children=items),  # Container for callback
                html.P(id=f"{self.id}-status", children="Click items!", style={'marginTop': '10px'})
            ]
        )


