import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import custom_components as cc



MODELS = ['Linear Regressor', 'Ridge', 'Lasso']
DATES = ["2018-01-05 00:00:00", "2018-01-05 01:00:00", "2018-01-05 02:00:00", "2018-01-05 03:00:00", "2018-01-05 04:00:00", "2018-01-05 05:00:00"]
RETRY_NUMBER = [10,20,30]
MASSES = [int(i) for i in range(100)]



layout = html.Div(
    [
        html.H1('Chemical mass balance'),
        html.Div([
        dcc.Dropdown(
            id='model-dropdown',
            options=[{'label':model, 'value':model} for model in MODELS],
            value = 'Lasso'
            ),
            ],style={'width': '33%', 'display': 'inline-block'}),
        html.Div([
        dcc.Dropdown(
            id='start-date-dropdown',
            options=[{'label':date, 'value':date} for date in DATES],
            value = "2018-01-05 11:00:00"
            ),
            ],style={'width': '33%', 'display': 'inline-block'}),
        html.Div([
        dcc.Dropdown(
            id='end-date-dropdown',
            options=[{'label':date, 'value':date} for date in DATES],
            value = "2018-01-31 01:00:00"
            ),
            ],style={'width': '33%', 'display': 'inline-block'}),




        dbc.Row(
            [
                html.Div(
                    [
                    cc.ChartCard("alpha-evolution", "HOA"),
                ],style={'width': '50%', 'display': 'inline-block'}),
                html.Div(
                    [
                    cc.ChartCard("beta-evolution", "BBOA"),
                ],style={'width': '50%', 'display': 'inline-block'}),
            ]
        ),
        dbc.Row(
            [
                html.Div(
                    [
                    cc.ChartCard("gamma-evolution", "MO-OOA"),
                ],style={'width': '50%', 'display': 'inline-block'}),
                html.Div(
                    [
                    cc.ChartCard("theta-evolution", "LO-OOA"),
                ],style={'width': '50%', 'display': 'inline-block'}),
            ]
        ),
        dbc.Row(
            [
                html.Div(
                    [
                    cc.ChartCard("MAE-error", "MAE error"),
                ],style={'width': '50%', 'display': 'inline-block'}),
                html.Div(
                    [
                    cc.ChartCard("MSE-error", "MSE error"),
                ],style={'width': '50%', 'display': 'inline-block'}),
            ]
        ),


        html.Hr(),


        html.Div([
        dcc.Dropdown(
            id='Time',
            options=[{'label':date, 'value':date} for date in DATES],
            value = "2018-01-06 17:00:00"
            ),
            ],style={'width': '50%', 'display': 'inline-block'}),

        dbc.Row(
            [
                html.Div(
                    [
                    cc.ChartCard("signal-reconstitution", "Mass spectrum reconstituton"),
                ],style={'width': '100%', 'display': 'inline-block'}),
            ]
        ),


        html.Hr(),


        html.Div([
        dcc.Dropdown(
            id='mass1',
            options=[{'label':mass, 'value':mass} for mass in MASSES],
            value = 18
            ),
            ],style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
        dcc.Dropdown(
            id='mass2',
            options=[{'label':mass, 'value':mass} for mass in MASSES],
            value = 44
            ),
            ],style={'width': '50%', 'display': 'inline-block'}),

        dbc.Row(
            [
                html.Div(
                    [
                    cc.ChartCard("mass1-error", "Error by mass"),
                ],style={'width': '50%', 'display': 'inline-block'}),
                html.Div(
                    [
                    cc.ChartCard("mass2-error", "Error by mass"),
                ],style={'width': '50%', 'display': 'inline-block'}),
            ]
        ),


        dbc.Row(
            [
                html.Div(
                    [
                    cc.ChartCard("mass-global-error", "Error on masses"),
                ],style={'width': '100%', 'display': 'inline-block'})
            ]
        ),


        html.Hr(),


        html.Div([
        dcc.Dropdown(
            id='retry-dropdown',
            options=[{'label':num, 'value':num} for num in RETRY_NUMBER],
            value = 10
            ),
            ],style={'width': '25%', 'display': 'inline-block'}),


        dbc.Row(
            [
                html.Div(
                    [
                    cc.ChartCard("alpha-evolution-retry", "HOA"),
                ],style={'width': '50%', 'display': 'inline-block'}),
                html.Div(
                    [
                    cc.ChartCard("beta-evolution-retry", "BBOA"),
                ],style={'width': '50%', 'display': 'inline-block'}),
            ]
        ),
        dbc.Row(
            [
                html.Div(
                    [
                    cc.ChartCard("gamma-evolution-retry", "MO-OOA"),
                ],style={'width': '50%', 'display': 'inline-block'}),
                html.Div(
                    [
                    cc.ChartCard("theta-evolution-retry", "LO-OOA"),
                ],style={'width': '50%', 'display': 'inline-block'}),
            ]
        ),

    ])
