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
        html.Button('Flip', id='flip-button')
    ]),

    dcc.Graph(
        id='graph',
    ),

    dcc.Interval(
        id='interval-component',
        interval=1*10,
        n_intervals=0
    )
])

@app.callback(Output('memory', 'data'),
              [Input('step-button', 'n_clicks'),
               Input('interval-component', 'n_intervals')],
              [State('memory', 'data')])
def on_click(n_clicks, n_intervals, data):
    if n_clicks is None:
        raise PreventUpdate

    # print("updating data")

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
    # print("updating figure")

    return {
        'data': [
            go.Scatter(x=data[0]['x'], y=data[0]['y'], mode='markers')
        ],
        'layout': go.Layout(
            xaxis=dict(
                range=[-100, 100]
            ),
            yaxis=dict(
                range=[-100, 100]
            )
        )
    }

@app.callback(
    Output('interval-component', 'max_intervals'),
    [Input('flip-button', 'n_clicks')],
    [State('interval-component', 'max_intervals')]
)
def flip(n_clicks, max_intervals):
    if n_clicks is None:
        raise PreventUpdate
    print("flipped")
    if max_intervals == -1:
        return 1
    else:
        return -1

if __name__ == '__main__':
    app.run_server(debug=True, port=8077, threaded=True)