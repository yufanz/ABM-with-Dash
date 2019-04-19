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


external_stylesheets = ['https:#codepen.io/chriddyp/pen/bWLwgP.css']
# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.GRID, external_stylesheets])
# app = dash.Dash(__name__, external_stylesheets=[external_stylesheets])


########################
# Global Variables
########################
initial_wealth = 100
interval = 10
delay = 10
n_agents = 200
xaxis_max = 5*initial_wealth

colors = [
	'#1f77b4',	# muted blue
    '#ff7f0e',  # safety orange
    '#2ca02c',  # cooked asparagus green
    '#d62728',  # brick red
    '#9467bd',  # muted purple
    '#8c564b',  # chestnut brown
    '#e377c2',  # raspberry yogurt pink
    '#7f7f7f',  # middle gray
    '#bcbd22',  # curry yellow-green
    '#17becf'   # blue-teal
]

initial_data = [{
    'x': [initial_wealth for i in range(n_agents)],
    'y': [i+1 for i in range(n_agents)]
}]

histogram_layout = go.Layout(
    xaxis=dict(
        range=[0, xaxis_max]
    ),
    yaxis=dict(
        range=[0, 1]
    ),
    hovermode='closest'
)

scatter_plot_layout = go.Layout(
    xaxis=dict(
        range=[0, xaxis_max]
    ),
    yaxis=dict(
        range=[0, n_agents]
    ),
    hovermode='closest'
)

def get_quantiles(x):
    y = numpy.sort(x)
    bottom_fifty_pct = sum(y[:int(n_agents/2)])
    top_10_pct = sum(y[int(n_agents*9/10):])
    return bottom_fifty_pct, top_10_pct

def get_total_wealth(initial_wealth, n_agents):

	return initial_wealth*n_agents

########################
# Layout
########################
app.layout = html.Div([

    dcc.Store(id='data'),

    dcc.Store(id='quantiles'),

    dcc.Store(id='color'),

    dcc.Interval(id='interval',
        interval=interval,
        max_intervals=0,
        n_intervals=0,
    ),

    dbc.Container([
    	dbc.Row([
    		dbc.Col([
    			html.Button('Step', id='step_button', n_clicks=0),
	    		html.Button('Play', id='play_button'),
	    		html.Button('Group',id='group_button')
    		]),
    		dbc.Col(dcc.Dropdown(id='group',
		    	options=[
		    		{'label': 'Top 10%', 'value': 90},
		    		{'label': 'Top 25%', 'value': 75},
		    		{'label': 'Bottom 25%', 'value': 25},
		    		{'label': 'Bottom 10%', 'value': 10}
		    	],
		    	value=10
		    ))
    	])
    ]),

    dbc.Container([
    	dbc.Row([
    		dbc.Col(
    			dcc.Graph(id='scatter_plot',
			        figure={
			            'data': [go.Scatter(
			                x=initial_data[0]['x'], 
			                y=initial_data[0]['y'], 
			                mode='markers')],
			            'layout': scatter_plot_layout
			        }
			    )
    		),
    		dbc.Col([
			    daq.LEDDisplay(id='n_iterations',
			        label='Iterations',
			        value=0,
			    ),

			    daq.LEDDisplay(id='bottom_50_pct',
			        label='Wealth of bottom 50%',
			        value=initial_wealth*n_agents*0.5,
			    ),

			    daq.LEDDisplay(id='top_10_pct',
			        label='Wealth of top 10%',
			        value=initial_wealth*n_agents*0.1,
			    ),

			    daq.LEDDisplay(id='total_wealth',
			        label='Total wealth',
			        value=get_total_wealth(initial_wealth, n_agents),
			    ),
    		])
    	])
    ]),

    dbc.Container([
    	dbc.Row([
    		dbc.Col([
    			dcc.Graph(id='histogram',
			        figure={
			            'data': [go.Histogram(
			                x=initial_data[0]['x'], 
			                xbins=dict(start=0, end=xaxis_max, size=5), 
			                autobinx = False,
			                histnorm='probability')
			            ],
			            'layout': histogram_layout
			        }
			    ),
			]),
			dbc.Col([
			    dcc.Graph(id='time_series',
			    	figure={
			    		'data': [
			    			go.Scatter(x=[0], y=[initial_wealth*n_agents*0.5]),
			    			go.Scatter(x=[0], y=[initial_wealth*n_agents*0.1])
			    		]
			    	}
			    )
    		])
    	])
    ])
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
	Output('color', 'data'),
	[Input('group_button', 'n_clicks')],
	[State('data', 'data'),
	 State('group', 'value')])
def group(n_clicks, data, group):

	if n_clicks is None or data is None:
		raise PreventUpdate

	argsort = numpy.argsort(data[0]['x'])
	length = len(data[0]['x'])
	result = [False]*length

	if group == 90:
		for i in range(int(n_agents * 0.9), length):
			result[argsort[i]] = True
	elif group == 75:
		for i in range(int(n_agents * 0.75), length):
			result[argsort[i]] = True
	elif group == 25:
		for i in range(int(n_agents * 0.25)):
			result[argsort[i]] = True
	elif group == 10:
		for i in range(int(n_agents * 0.1)):
			result[argsort[i]] = True
	else:
		raise PreventUpdate

	return result

@app.callback(
    [Output('histogram', 'figure'),
     Output('scatter_plot', 'figure')],
    [Input('data', 'data'),
     Input('color', 'data')],
    [State('interval', 'n_intervals')])
def update_figure(data, color, n_intervals):

    if data is None or n_intervals % delay != 0:
        raise PreventUpdate

    histogram = {
        'data': [go.Histogram(
            x=data[0]['x'], 
            xbins=dict(start=0, end=500, size=10), 
            autobinx = False, 
            histnorm='probability')],
        'layout': histogram_layout
    }

    color = color or [False]*len(data[0]['x'])
    marker_color = [colors[0]]*len(data[0]['x'])
    for c in range(len(color)):
    	if color[c]:
    		marker_color[c] = colors[1]

    scatter_plot = {
        'data': [go.Scatter(
            x=data[0]['x'], 
            y=data[0]['y'], 
            mode='markers',
            marker=dict(color=marker_color))],
        'layout': scatter_plot_layout
    }

    return histogram, scatter_plot

@app.callback(
	Output('time_series', 'figure'),
	[Input('quantiles', 'data')])
def update_quantiles(quantiles):

	if quantiles is None or len(quantiles[0]['bottom_50_pct']) % delay != 0:
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

server = app.server
if __name__ == '__main__':
    app.run_server(debug=True, port=8077, threaded=True)