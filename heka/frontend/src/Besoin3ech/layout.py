import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import custom_components as cc
from Besoin3ech.helpers import *
import dash_table
from datetime import datetime as dt
from datetime import date




layout = html.Div(
    [
        html.H1('Echantillons analysées'),
        html.Div(id='non-displayed-sample'),

        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.DatePickerRange(
                            id='my-date-picker-range-ech',
                            min_date_allowed=dt(2011, 1, 1),
                            display_format='DD-MM-YYYY',
                            initial_visible_month=dt(2012, 1, 1),
                            # start_date=dt(2018, 1, 1).date(),
                            # end_date=dt(2018, 1, 31).date(),
                            clearable=True,
                            updatemode='bothdates'
                        ),
                ],width=8),
                dbc.Col(
                    [
                        html.Button(
                            'Appliquer filtre',
                            id='launch-analysis-ech'
                        ),
                        html.Div(id='test', style={'display': 'none'}),
                ],width=4),
            ]
        ),

        html.Br(),

        dbc.Row([
            dbc.Col([
                html.H4('Derniers échantillons en base'),
                html.Div([
                        dash_table.DataTable(
                            id='treated-samples',
                            columns=[{'name': 'Charging ...', 'id': 'Charging ...'}],
                            filter_action="native",
                            sort_action="native",
                            sort_mode="multi",
                            selected_rows=[],
                            page_action="native",
                            page_size= 10
                        ),
                    ]),
                ], width=8),
            dbc.Col([
                html.Br(),
                html.Div(id='buttons-sample', children=[
                    html.Button(
                        'Blacklister',
                        id='blacklist-sample',
                        style={
                            'width': '50%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                    ),
                    html.Div(id='output-data-blacklist')
                    ]),
                ], width=4)

            ]),


        dbc.Row([
            dbc.Col([
                html.H4('Echantillons blacklistés'),
                html.Div([
                        dash_table.DataTable(
                            id='black-listed-samples',
                            columns=[{'name': 'Charging ...', 'id': 'Charging ...'}],
                            filter_action="native",
                            sort_action="native",
                            sort_mode="multi",
                            selected_rows=[],
                            page_action="native",
                            page_size= 10
                        ),
                    ]),
                ], width=8),
            dbc.Col([
                html.Br(),
                html.Div(id='buttons-blacklist-sample', children=[
                    html.Button(
                        'Whitelister',
                        id='white-list-sample',
                        style={
                            'width': '50%',
                            'height': '60px',
                            'lineHeight': '60px',
                            'borderWidth': '1px',
                            'borderRadius': '5px',
                            'textAlign': 'center',
                            'margin': '10px'
                        },
                    ),
                    html.Div(id='output-data-whitelist')
                    ]),
                ], width=4)

            ]),


        dbc.Row([

            dbc.Col(
                [
                html.H4('Dernières tâches lancées'),
                cc.ChartCard("launched-analysis", "Tâches lancées"),
            ],width=12),

            ]),

        # html.Div(id='selected-row-ids-samples'),
        
        html.Div(id='intermediate-value-sample', style={'display': 'none'}),
        html.Div(id='intermediate-value-sample-blacklisted', children=[html.Button('hidden', id='hidden-button')], style={'display': 'none'}),
        html.Div(id='intermediate-value-sample-blacklisted-1', children=[html.Button('hidden', id='hidden-button-1')], style={'display': 'none'}),
        html.Div(id='intermediate-value-sample-blacklisted', style={'display': 'none'}),
        html.Div(id='test', style={'display': 'none'})
        ])