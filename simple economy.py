import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go

from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

import random

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([

    dcc.Store(
        id='memory'
    ),

    html.Div([
        html.Button('Step', id='step-button'),
    ]),

    dcc.Graph(
        id='graph',
    )
])

@app.callback(Output('memory', 'data'),
              [Input('step-button', 'n_clicks')],
              [State('memory', 'data')])
def on_click(n_clicks, data):
    if n_clicks is None:
        raise PreventUpdate

    data = data or [
        {'x': [10 for i in range(100)], 
         'y': [i for i in range(100)]},
    ]

    newX = [i - 1 for i in data[0]['x']]
    for i in range(len(newX)):
        idx = random.randint(0, len(newX)-1)
        newX[idx] = newX[idx] + 1

    return [{'x': newX, 'y': data[0]['y']}]

# output the stored clicks in the table cell.
@app.callback(Output('graph', 'figure'),
              [Input('memory', 'modified_timestamp')],
              [State('memory', 'data')])
def on_data(ts, data):
    if ts is None:
        raise PreventUpdate

    # data = data or {}
    # return data

    return {
        'data': [
            go.Scatter(x=data[0]['x'], y=data[0]['y'], mode='markers')
        ],
        'layout': go.Layout(
            xaxis=dict(
                range=[-10, 50]
            ),
            yaxis=dict(
                range=[0, 100]
            )
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True, port=8077, threaded=True)