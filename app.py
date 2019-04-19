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
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.GRID])
# app = dash.Dash(__name__, external_stylesheets=[external_stylesheets])
# app = dash.Dash(__name__)

########################
# Global Variables
########################
colors = [
    '#1f77b4',  # muted blue
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
initial_wealth = 100
interval = 10
delay = 10
n_agents = 100
xaxis_max = 5*initial_wealth
total_wealth = initial_wealth * n_agents

agents = numpy.arange(1, n_agents+1)
initial_data = [{'x': [initial_wealth for i in range(n_agents)]}]

histogram_layout = go.Layout(
    xaxis=dict(
        range=[0, xaxis_max],
        title="Wealth"
    ),
    yaxis=dict(
        range=[0, 0.5],
        title="Density"
    ),
    hovermode='closest'
)
scatter_plot_layout = go.Layout(
    xaxis=dict(
        range=[0, xaxis_max],
        title="Wealth"
    ),
    yaxis=dict(
        range=[0, n_agents+10],
        title="Person"
    ),
    hovermode='closest'
)
time_series_layout = go.Layout(
	xaxis=dict(
        title="Time"
    ),
    yaxis=dict(
        title="Aggregate Wealth"
    ),
)

def get_quantiles(x):
    y = numpy.sort(x)
    bottom_fifty_pct = sum(y[:int(n_agents/2)])
    top_10_pct = sum(y[int(n_agents*9/10):])
    return bottom_fifty_pct, top_10_pct

########################
# Layout
########################
app.layout = html.Div([

	# html.P("This is an implementation and extension to the classical agent-based model, Simple Economy, in Uri Wilensky's Introduction to Agent-Based Modeling."),

	# html.P("The rules are simple. Everyone in an economy starts with 100 dollars, and gives one to a random other every day as long as he/she has any."),

	# html.P("The interesting observation is that very soon, despite the fair rules, the wealthiest 10 percent of the population will have more than 50 percent of all the wealth in the economy."),

	# html.P("Click the step-button to see what happens after a day. Click the play-button to run the simulation infinitely, and to pause it."),

	# html.P("You can also group an income group while running the simulation, to see that the rich don't stay rich, and the poor don't actually stay poor, given time."),

    dcc.Markdown('''
    ## A Mixed Recovery
    Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
    '''.replace('  ', ''), className='container',
    containerProps={'style': {'maxWidth': '650px'}}),

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
            dbc.Col([html.Button('Step', id='step_button', n_clicks=0)]),
            dbc.Col([html.Button('Play', id='play_button')]),
            dbc.Col([html.Button('Group',id='group_button')]),
            dbc.Col([dcc.Dropdown(id='group',
                        options=[
                            {'label': 'Top 10%', 'value': 90},
                            {'label': 'Top 25%', 'value': 75},
                            {'label': 'Bottom 25%', 'value': 25},
                            {'label': 'Bottom 10%', 'value': 10}
                        ],
                        value=90
                    )]),
        ]),

        dbc.Row([
            dbc.Col([
                dcc.Graph(id='scatter_plot',
                    figure={
                        'data': [go.Scatter(
                            x=initial_data[0]['x'], 
                            y=agents, 
                            mode='markers')],
                        'layout': scatter_plot_layout
                    }
                )
            ])
        ]),

        dbc.Row([
            dbc.Col([
                daq.LEDDisplay(
                    id='n_iterations',
                    label='Iterations',
                    value=0,
                )
            ]),
            dbc.Col([
                daq.LEDDisplay(
                    id='bottom_50_pct',
                    label='Wealth of bottom 50%',
                    value=initial_wealth*n_agents*0.5,
                )
            ]),
            dbc.Col([
                daq.LEDDisplay(
                    id='top_10_pct',
                    label='Wealth of top 10%',
                    value=initial_wealth*n_agents*0.1,
                )
            ]),
            dbc.Col([
                daq.LEDDisplay(
                    id='total_wealth',
                    label='Total wealth',
                    value=total_wealth,
                )
            ])
        ]),

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
                            go.Scatter(x=[0], y=[initial_wealth*n_agents*0.5], name="Bottom 50%"),
                            go.Scatter(x=[0], y=[initial_wealth*n_agents*0.1], name="Top 10%")
                        ],
                        'layout': time_series_layout
                    }
                )
            ])
        ])

    ], className="container"),

   #  dbc.Container([
   #  	dbc.Row([
   #  		dbc.Col([
   #  			dcc.Graph(id='histogram',
			#         figure={
			#             'data': [go.Histogram(
			#                 x=initial_data[0]['x'], 
			#                 xbins=dict(start=0, end=xaxis_max, size=5), 
			#                 autobinx = False,
			#                 histnorm='probability')
			#             ],
			#             'layout': histogram_layout
			#         }
			#     ),
			# ]),
			# dbc.Col([
			#     dcc.Graph(id='time_series',
			#     	figure={
			#     		'data': [
			#     			go.Scatter(x=[0], y=[initial_wealth*n_agents*0.5], name="Bottom 50%"),
			#     			go.Scatter(x=[0], y=[initial_wealth*n_agents*0.1], name="Top 10%")
			#     		],
			#     		'layout': time_series_layout
			#     	}
			#     )
   #  		])
   #  	])
   #  ])
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
    data = [{'x': newX, 'y': agents}]

    return bottom_50_pct, top_10_pct, n_iterations, data, quantiles
    # return data, quantiles

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
	result = [False]*n_agents

	if group == 90:
		for i in range(int(n_agents * 0.9), n_agents):
			result[argsort[i]] = True
	elif group == 75:
		for i in range(int(n_agents * 0.75), n_agents):
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

    color = color or [False]*n_agents
    marker_color = [colors[0]]*n_agents
    for c in range(len(color)):
    	if color[c]:
    		marker_color[c] = colors[1]

    scatter_plot = {
        'data': [go.Scatter(
            x=data[0]['x'], 
            y=agents, 
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
			go.Scatter(x=n_indices, y=bottom_50_pcts, name="Bottom 50%"),
			go.Scatter(x=n_indices, y=top_10_pcts, name="Top 50%"),
		],
		'layout': time_series_layout
	}

server = app.server
if __name__ == '__main__':
    app.run_server(debug=True, port=8077, threaded=True)