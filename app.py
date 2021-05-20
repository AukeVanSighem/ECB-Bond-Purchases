import dash
import dash_html_components as html
import dash_core_components as dcc
from plotly.subplots import make_subplots
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import numpy as np
import pandas as pd

from test_graphs import make_plot # Import the figures you made. Convert your notebook to a .py file

app = dash.Dash(__name__, title="ECB green bonds", external_stylesheets=[dbc.themes.LUMEN])
server = app.server # Needed for Heroku to deploy

# Figure1: green bonds
fig = make_subplots(rows=1,cols=1)
fig.add_trace(
    go.Scatter(x=np.arange(0,10,1), y=2*np.arange(0,10,1)+np.random.randn())
)
fig.update_layout(margin=dict(l=1, r=1, b=1, t=1))

# Add dropdown box for fig
dropdown = dcc.Dropdown(id="id_currency",
                        options = [
                            {"label":"CHF","value":"CHF"},
                            {"label":"CHF1","value":"CHF1"},
                            {"label":"CHF2","value":"CHF2"},
                            {"label":"CHF3","value":"CHF3"}
                        ], value="CHF")

# Create an input Group --> Combine all the input feelds together: can type or dropdown
input_groups = dbc.Row(dbc.Col(html.Div([
    dbc.InputGroup([
        dbc.InputGroupAddon("T0", addon_type="prepend"), # comes before the input field
        dbc.Input(id="id_start_date", value="2008-01-01")
    ], className="mb-3"),
    dbc.InputGroup([
        dbc.InputGroupAddon("T1", addon_type="prepend"), # comes before the input field
        dbc.Input(id="id_end_date", value="2021-01-01")
    ], className="mb-3"),
    dbc.InputGroup([
        dbc.InputGroupAddon("Nbr Mixtures", addon_type="prepend"), # comes before the input field
        dbc.Input(id="id_nbr_mixtures", value=3, type="number") # add type if not text
    ], className="mb-3"),
    dropdown 
])))

section1 = html.Div(children=[html.H1(children="Green bonds"),
                                html.H2(children="Data source: ECB and Euronext"),
                                html.H4(children=".", id="id_title")],
                      style={"textAlign":"center", "color":"blue"})

# figure1 = dcc.Graph(id="id_graph", figure=fig)

# Layout - Bootstrap
app.layout = dbc.Container([section1,
                            html.Hr(), # Horizontal line
                            dbc.Row(
                                [dbc.Col(input_groups, md=2),
                                dbc.Col(dcc.Graph(id="id_graph", figure=fig), md=10)],align="center"
                            )], fluid=True)

# app.layout = html.Div(children=[section1, figure1])

@app.callback(
    Output("id_title", "children"),
    Output("id_graph", "figure"),
    [
        Input("id_currency", "value"),
        Input("id_start_date", "value"),
        Input("id_end_date", "value"),
        Input("id_nbr_mixtures", "value")
    ]
)

def update_chart(currency_value,start_date,end_date,nbr):
    try: # Make sure system still works if user gives a wrong input
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    except:
        fig = make_subplots(rows=1, cols=1)
        fig.add_trace(
            go.Scatter(x=np.arange(0,10,1),
                       y=np.arange(0,10,1)*2 + np.random.randn(),
                       name='Example'),
            row=1, col=1)
        fig.update_layout(width=1500)
        return 'Error in Input' , fig


    if nbr is None:
        nbr = 3

    nbr = max(1,min(5,nbr))
    params = {}
    params['start_date'] = start_date
    params['end_date'] = end_date
    params['currency'] = currency_value
    params['nbr_mixtures'] = nbr
    params['periods'] = 1
    fig = make_plot(params)

    return 'Gaussian Mixtures for EUR' + currency_value + \
           ' (' + str(nbr) + ' Mixtures) ' + start_date.strftime('%Y-%m-%d') + '->' + end_date.strftime('%Y-%m-%d') , fig

if __name__ == "__main__":
    app.run_server(debug=True) # Put False when deploy