import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go

from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

import random

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

initial_data = [{
    'x': [10 for i in range(100)],
    'y': [i for i in range(100)]
}]

initial_layout = go.Layout(
    xaxis=dict(
        range=[-100, 100]
    ),
    yaxis=dict(
        range=[-100, 100]
    )
)

app.layout = html.Div([

    dcc.Store(
        id='memory'
    ),

    html.Div([
        html.Button('Step', id='step-button'),
        html.Button('Play / Pause', id='play-button')
    ]),

    dcc.Graph(
        id='scatter-plot',
        figure={
            'data': [go.Scatter(x=initial_data[0]['x'], y=initial_data[0]['y'], mode='markers')],
            'layout': initial_layout
        }
    ),

    dcc.Interval(
        id='interval',
        interval=1*10,
        n_intervals=0,
        max_intervals=0
    )
])


@app.callback(
    Output('memory', 'data'),
    [Input('step-button', 'n_clicks'),
     Input('interval', 'n_intervals'),
     Input('interval', 'max_intervals')],
    [State('memory', 'data')])
def step(n_clicks, n_intervals, max_intervals, data):

    if n_clicks is None and max_intervals == 0:
        raise PreventUpdate

    data = data or initial_data

    newX = [i - 1 for i in data[0]['x']]
    for i in range(len(newX)):
        idx = random.randint(0, len(newX)-1)
        newX[idx] = newX[idx] + 1

    return [{'x': newX, 'y': data[0]['y']}]


@app.callback(
    Output('interval', 'max_intervals'),
    [Input('play-button', 'n_clicks')],
    [State('interval', 'max_intervals')])
def play(n_clicks, max_intervals):

    if n_clicks is None:
        raise PreventUpdate
    if max_intervals == -1:
        return 0
    else:
        return -1


@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('memory', 'data')])
def update_figure(data):

    return {
        'data': [go.Scatter(x=data[0]['x'], y=data[0]['y'], mode='markers')],
        'layout': initial_layout
    }


if __name__ == '__main__':
    app.run_server(debug=True, port=8077, threaded=True)