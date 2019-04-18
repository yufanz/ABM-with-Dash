# app.py

########################
# Dash modules
########################
import dash
import dash_bootstrap_components        as dbc
import dash_core_components             as dcc
import dash_daq                         as daq
import dash_html_components             as html
from dash.dependencies                  import Input, Output, State
from dash.exceptions                    import PreventUpdate

########################
# Plotly modules
########################
import plotly.graph_objs                as go

########################
# Python modules
########################
import numpy
import random
#import os


#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])


########################
# Global Variables
########################
initial_wealth = 100
interval = 100
delay = 10
n_agents = 200
xaxis_max = 5*initial_wealth

layout = go.Layout(
    xaxis=dict(
        range=[0, xaxis_max]
    ),
    yaxis=dict(
        range=[0, n_agents]
    )
)

########################
# Derivatives
########################
initial_data = [{
    'x': [initial_wealth for i in range(n_agents)],
    'y': [i+1 for i in range(n_agents)]
}]

########################
# Functions
########################
def get_quantiles(x):
    y = numpy.sort(x)
    bottom_fifty_pct = sum(y[:int(n_agents/2)])
    top_10_pct = sum(y[int(n_agents*9/10):])
    return bottom_fifty_pct, top_10_pct

########################
# Layout
########################
app.layout = html.Div([

    dcc.Store(
        id='data'
    ),

    dcc.Store(
    	id='quantiles'
    ),

    dcc.Interval(
        id='interval',
        interval=interval,
        max_intervals=0,
        n_intervals=0,
    ),

    html.Button('Step',
        id='step_button',
        n_clicks=0,
    ),

    html.Button('Play',
        id='play_button',
    ),

    daq.LEDDisplay(
        id='n_iterations',
        label='Iterations',
        value=0,
    ),

    daq.LEDDisplay(
        id='bottom_50_pct',
        label='Wealth of bottom 50%',
        value=initial_wealth*n_agents*0.5,
    ),

    daq.LEDDisplay(
        id='top_10_pct',
        label='Wealth of top 10%',
        value=initial_wealth*n_agents*0.1,
    ),

    dcc.Graph(
        id='scatter_plot',
        figure={
            'data': [go.Scatter(
                x=initial_data[0]['x'], 
                y=initial_data[0]['y'], 
                mode='markers')],
            'layout': layout
        }
    ),

    dcc.Graph(
        id='histogram',
        figure={
            'data': [go.Histogram(
                x=initial_data[0]['x'], 
                xbins=dict(start=0, end=xaxis_max, size=5), 
                autobinx = False,
                histnorm='probability')
            ],
        }
    ),

    dcc.Graph(
    	id='time_series',
    	figure={
    		'data': [
    			go.Scatter(x=[0], y=[initial_wealth*n_agents*0.5]),
    			go.Scatter(x=[0], y=[initial_wealth*n_agents*0.1])
    		]
    	}
    )
])

########################
# Callbacks
########################

@app.callback(
    [Output('bottom_50_pct', 'value'),
     Output('top_10_pct', 'value'),
     Output('n_iterations', 'value'),
     Output('data', 'data'),
     Output('quantiles', 'data')],
    [Input('interval', 'max_intervals'),
     Input('interval', 'n_intervals'),
     Input('step_button', 'n_clicks')],
    [State('data', 'data'),
     State('quantiles', 'data')])
def step(max_intervals, n_intervals, n_clicks, data, quantiles):

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
        newX[random.randint(0,n_agents-1)] += 1

    bottom_50_pct, top_10_pct = get_quantiles(newX)
    if quantiles is None:
      quantiles = [{
          'bottom_50_pct': [bottom_50_pct],
          'top_10_pct': [top_10_pct]
      }]
    else:
      quantiles = [{
          'bottom_50_pct': quantiles[0]['bottom_50_pct'] + [bottom_50_pct],
          'top_10_pct': quantiles[0]['top_10_pct'] + [top_10_pct]
      }]

    n_iterations = n_clicks + n_intervals
    data = [{'x': newX, 'y': data[0]['y']}]

    return bottom_50_pct, top_10_pct, n_iterations, data, quantiles

@app.callback(
    Output('interval', 'max_intervals'),
    [Input('play_button', 'n_clicks')],
    [State('interval', 'max_intervals')])
def play(n_clicks, max_intervals):

    if n_clicks is None:
        raise PreventUpdate
    if max_intervals == -1:
        return 0
    else:
        return -1

@app.callback(
    [Output('histogram', 'figure'),
     Output('scatter_plot', 'figure')],
    [Input('data', 'data')],
    [State('interval', 'n_intervals')])
def update_figure(data, n_intervals):

    if data is None or n_intervals % delay != 0:
        raise PreventUpdate

    histogram = {
        'data': [go.Histogram(
            x=data[0]['x'], 
            xbins=dict(start=0, end=500, size=10), 
            autobinx = False, 
            histnorm='probability')],
    }

    scatter_plot = {
        'data': [go.Scatter(
            x=data[0]['x'], 
            y=data[0]['y'], 
            mode='markers')],
        'layout': layout
    }

    # time_series = {
    # 	'data': [
    # 		go.Scatter(
    # 			x=range(0, len(quantiles[0]['bottom_50_pct'])-1), 
    # 			y=quantiles[0]['bottom_50_pct']),
    # 		go.Scatter(
    # 			x=range(0, len(quantiles[0]['top_10_pct'])-1), 
    # 			y=quantiles[0]['top_10_pct'])
    # 	]
    # }

    return histogram, scatter_plot #, time_series

@app.callback(
	Output('time_series', 'figure'),
	[Input('quantiles', 'data')],
	[State('interval', 'n_intervals')])
def update_quantiles(quantiles, n_intervals):

	if quantiles is None or n_intervals % delay != 0:
		raise PreventUpdate

	bottom_50_pcts = quantiles[0]['bottom_50_pct']
	top_10_pcts = quantiles[0]['top_10_pct']
	n_indices = numpy.arange(len(bottom_50_pcts))

	return {
		'data': [
			go.Scatter(x=n_indices, y=bottom_50_pcts),
			go.Scatter(x=n_indices, y=top_10_pcts),
		]
	}

########################
# Markdowns
########################


server = app.server
if __name__ == '__main__':
    app.run_server(debug=True, port=8077, threaded=True)