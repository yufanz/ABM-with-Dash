import dash
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objs as go

from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate

import numpy, random

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# GLOBALS

num_of_agents = 500

initial_wealth = 100

initial_data = [{
    'x': [initial_wealth for i in range(num_of_agents)],
    'y': [i for i in range(num_of_agents)]
}]

scatter_plot_layout = go.Layout(
    xaxis=dict(
        range=[0, 500]
    ),
    yaxis=dict(
        range=[0, num_of_agents]
    )
)

histogram_layout = go.Layout(

)

# CORE

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
            'layout': scatter_plot_layout
        }
    ),

    dcc.Graph(
        id='histogram',
        figure={
            'data': [go.Histogram(
                        x=initial_data[0]['x'], 
                        xbins=dict(start=0, end=500, size=10), 
                        autobinx = False)],
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

    num_of_benefactors = 0
    newX = data[0]['x']
    for i in range(len(newX)):
        if newX[i] > 0:
            newX[i] -= 1
            num_of_benefactors += 1

    for i in range(num_of_benefactors):
        newX[random.randint(0,num_of_agents-1)] += 1

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
    [Output('scatter-plot', 'figure'),
     Output('histogram', 'figure')],
    [Input('memory', 'data')])
def update_figure(data):

    return {
        'data': [go.Scatter(x=data[0]['x'], y=data[0]['y'], mode='markers')],
        'layout': scatter_plot_layout
    }, {
        'data': [go.Histogram(
                        x=data[0]['x'], 
                        xbins=dict(start=0, end=500, size=10), 
                        autobinx = False)],
    }


if __name__ == '__main__':
    app.run_server(debug=True, port=8077, threaded=True)