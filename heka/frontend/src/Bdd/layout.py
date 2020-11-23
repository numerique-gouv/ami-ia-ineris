import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import custom_components as cc
from Besoin1.helpers import *
import dash_table




layout = html.Div(
    [


    dcc.Tabs([

    dcc.Tab(label='Echantillons', children=[

        html.Div([
                dash_table.DataTable(
                    id='table-echantillon',
                    columns=[{'name': 'test', 'id': 'test'}],
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    selected_rows=[],
                    page_action="native",
                    page_size= 10
                ),
            ]),


        html.Br(),
        html.Br(),
        html.Br(),
        html.Br(),


        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(id='buttons-echantillon', children=[
                            dcc.Upload(
                                id='upload-data-echantillon',
                                children=html.Div([
                                    'Drag and Drop or ',
                                    html.A('Select Files')
                                ]),
                                style={
                                    'width': '100%',
                                    'height': '60px',
                                    'lineHeight': '60px',
                                    'borderWidth': '1px',
                                    'borderStyle': 'dashed',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin': '10px'
                                },
                                # Allow multiple files to be uploaded
                                multiple=True
                            ),
                        ]),

                ],width=6),
                dbc.Col(
                    [
                        html.Div(id='buttons-launch-analysis', children=[
                            html.Button(
                                'Lancer analyse',
                                id='launch-analysis',
                                style={
                                    'width': '100%',
                                    'height': '60px',
                                    'lineHeight': '60px',
                                    'borderWidth': '1px',
                                    'borderRadius': '5px',
                                    'textAlign': 'center',
                                    'margin': '10px'
                                },
                            ),

                            dbc.Row([
                                dbc.Col([
                                    html.Label('Threshold positif'),
                                    dcc.Input(id='threshold-positif', value=10000),
                                ],width=4),
                                dbc.Col([
                                    html.Label('Threshold negatif'),
                                    dcc.Input(id='threshold-negatif', value=1000),
                                ],width=4),
                                dbc.Col([
                                    html.Label('Base de données'),
                                    dcc.Dropdown(
                                        options=[
                                            {'label': 'INERIS', 'value': 'INERIS'},
                                            {'label': 'Agilent', 'value': 'Agilent'},
                                        ],
                                        value=['INERIS', 'Agilent'],
                                        multi=True
                                    )  
                                ],width=4),
                            ]),

                            html.Div(id='selected-row-ids-echantillon'),
                            html.Div(id='selected-row-ids-echantillon-test'),

                        ]),

                ],width=6)
            ]
        ),

        
        html.Div(id='output-data-upload'),
        html.Div(id='intermediate-value-echantillon', style={'display': 'none'})

        ]),


        dcc.Tab(label='Analyses', children=[

        html.Div(id='non-displayed'),
        html.Div([
                dash_table.DataTable(
                    id='table-analysis',
                    columns=[{'name': 'test', 'id': 'test'}],
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    selected_rows=[],
                    page_action="native",
                    page_size= 10
                ),
            ]),

        html.Div(id='selected-row-ids-analysis'),


        html.Br(),

        html.Div(id='buttons-analysis', children=[
            html.Button(
                'Afficher paramètres',
                id='show-analysis',
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

        ]),

        html.Div(id='intermediate-value-analysis', style={'display': 'none'})

        ]),

        ])
        ])