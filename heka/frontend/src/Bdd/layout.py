import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import custom_components as cc
from Bdd.helpers import *
import dash_table




layout = html.Div(
    [




        html.H1('Base de données'),
        html.Div([
                dash_table.DataTable(
                    id='table-echantillon',
                    columns=[{'name': 'Charging ...', 'id': 'Charging ...'}],
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

                        html.Div(id='output-data-upload'),
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
                                        id='molecule-bdd',
                                        options=[],
                                        # value=['INERIS', 'Agilent'],
                                        multi=True
                                    )  
                                ],width=4),
                            ]),

                            html.Div(id='selected-row-ids-echantillon'),
                            html.Div(id='selected-row-ids-echantillon-test'),
                            dcc.ConfirmDialog(
                                id='confirm',
                                message='Danger danger! Are you sure you want to continue?',
                            ),
                        ]),

                ],width=6)
            ]
        ),

        
        html.Div(id='intermediate-value-echantillon', style={'display': 'none'}),
        html.Div(id='non-displayed')

        ])