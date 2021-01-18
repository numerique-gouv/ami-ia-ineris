import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import custom_components as cc
from Boucle_retour.helpers import *
import dash_table
import dash_table as dt
import dash_daq as daq


lvls = ['1', '2A', '2B', '3', '0', '']
df = get_df_full_query("""SELECT molecule_name FROM public.molecules GROUP BY 1 ORDER BY 1;""")
Meds = list(df['molecule_name'].values)

blobs = list_blobs()
names = [i['blob_name'].split('/')[-2]+'/'+i['blob_name'].split('/')[-1] for i in blobs if ((i['blob_name'][-4:] == 'mzML') and ("_Med" not in i['blob_name'].split('/')[-1]) and ("Pesticides" not in i['blob_name'].split('/')[-1]) and ("mix_perfluores" not in i['blob_name'].split('/')[-1]) and ("bisphenols" not in i['blob_name'].split('/')[-1]))]


modal_layout = html.Div([
        html.H1('Chromatogram'),
        # html.Div([
        # dcc.Dropdown(
        #     id='name-dropdown-modal',
        #     options=[{'label':name, 'value':name} for name in names]
        #     # ,value = 'POS/21-04-20-Mix_14_Med_allion_50_pos-1.mzML'
        #     ),
        #     ],style={'width': '49.25%', 'display': 'inline-block'}),
        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("chromatogram-modal", "Chromatogram"),
                ],width=8),
                dbc.Col(
                    [
                    html.Br(),
                    html.H4("Spectrum number", id="Nb_spectrum", className="h4 mb-4 text-gray-800"),
                    html.Div("", id="Nb_spectrum_value-modal"),
                    html.Br(),
                    html.H4("Acquistion mode", id="Acq_mode", className="h4 mb-4 text-gray-800"),
                    html.Div("", id="Acq_mode_value-modal"),
                    html.Br(),
                    html.H4("Ionisation mode", id="Ion_mode", className="h4 mb-4 text-gray-800"),
                    html.Div("", id="Ion_mode_value-modal"),
                ],width=4)
            ]
        ),

        html.Hr(),
        html.H1('Choosing the molecule to look for'),
        # dbc.Row(
        #     [
        #         dbc.Col(
        #             [
        #             dcc.Dropdown(
        #             id='name-dropdown-Mol-modal',
        #             options=[{'label':name, 'value':name} for name in Meds]
        #             ),                    
        #         ],width=4),
        #         dbc.Col(
        #             [
        #             dcc.Dropdown(
        #             id='name-dropdown-Source-modal',
        #             options=[]
        #             ),                    
        #         ],width=4),
        #         dbc.Col(
        #             [
        #             dcc.Dropdown(
        #             id='name-dropdown-Species-modal',
        #             options=[]
        #             ),                    
        #         ],width=4),
        #     ]
        # ),


        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("search-in-chromato-modal", "Search on chromatogram"),

                ],width=8),
                dbc.Col(
                    [
                    html.Br(),
                    html.H4("Mass", id="Mass", className="h4 mb-4 text-gray-800"),
                    html.Div("", id="Mass_value-modal"),
                    html.Br(),
                    html.H4("Retention time", id="RT-modal", className="h4 mb-4 text-gray-800"),
                    html.Div("", id="RT_value-modal"),
                    html.Br(),
                    html.H4("Extracted peaks", id="extracted-peaks-title-modal", className="h4 mb-4 text-gray-800"),
                    html.Div(
                                [
                                    dt.DataTable(id='datatable-peaks-modal', 
                                        columns = [{"id": 'Minute', "name": 'Minute'}, {"id": 'Peak value', "name": 'Peak value'}, {"id": 'Detected mass', "name": 'Detected mass'}],
                                        style_data={'whiteSpace': 'pre-line'}, 
                                        style_cell={'textAlign': 'left'})
                                ]
                            )
                ],width=4)
            ]
        ),

        html.Hr(),

        html.H1('Result of research'),
        # html.Div([],style={'width': '50.75%', 'display': 'inline-block'}),
        # html.Div([
        # dcc.Dropdown(
        #     id='opt-dropdown-spectrum-modal',
        #     ),
        #     ],style={'width': '49.25%', 'display': 'inline-block'}
        # ),
        # html.Div([],style={'width': '50.75%', 'display': 'inline-block'}),


        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("search-fragment-10-only-fragment-modal", "Fragmentation with 10eV with fragment only"),
                ],width=4),
                dbc.Col(
                    [
                    cc.ChartCard("search-fragment-20-only-fragment-modal", "Fragmentation with 20eV with fragment only"),
                ],width=4),
                dbc.Col(
                    [
                    cc.ChartCard("search-fragment-40-only-fragment-modal", "Fragmentation with 40eV with fragment only"),
                ],width=4),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("fragment-10-modal", "Fragmentation with 10eV of molecule to look for"),
                ],width=4),
                dbc.Col(
                    [
                    cc.ChartCard("fragment-20-modal", "Fragmentation with 20eV of molecule to look for"),
                ],width=4),
                dbc.Col(
                    [
                    cc.ChartCard("fragment-40-modal", "Fragmentation with 40eV of molecule to look for"),
                ],width=4),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                    html.Div(
                        [
                            html.H4("10 eV fragmentation similarity", id="fragment-10-similarity-title", className="h4 mb-4 text-gray-800"),
                            html.Div("Cosine similarity", id="fragment-10-cosine-text-modal"),
                            html.Div("", id="fragment-10-similarity-modal"),
                            html.Div("Cosine of root square similarity", id="fragment-10-cosine-root-text-modal", style={'display': 'none'}),
                            html.Div("", id="fragment-10-similarity-cosine-root-modal", style={'display': 'none'}),
                            html.Div("Pearson similarity", id="fragment-10-pearson-text-modal", style={'display': 'none'}),
                            html.Div("", id="fragment-10-similarity-pearson-modal", style={'display': 'none'}),
                            html.Div("Scholle similarity", id="fragment-10-scholle-text-modal"),
                            html.Div("", id="fragment-10-similarity-scholle-modal"),                            
                        ]
                        ),
                ],width=4),
                dbc.Col(
                    [
                    html.Div(
                        [
                            html.H4("20 eV fragmentation similarity", id="fragment-20-similarity-title", className="h4 mb-4 text-gray-800"),
                            html.Div("Cosine similarity", id="fragment-20-cosine-text"),
                            html.Div("", id="fragment-20-similarity-modal"),
                            html.Div("Cosine of root square similarity", id="fragment-20-cosine-root-text", style={'display': 'none'}),
                            html.Div("", id="fragment-20-similarity-cosine-root-modal", style={'display': 'none'}),
                            html.Div("Pearson similarity", id="fragment-20-pearson-text", style={'display': 'none'}),
                            html.Div("", id="fragment-20-similarity-pearson-modal", style={'display': 'none'}),
                            html.Div("Scholle similarity", id="fragment-20-scholle-text"),
                            html.Div("", id="fragment-20-similarity-scholle-modal"),                    
                        ]
                        ),
                ],width=4),
                dbc.Col(
                    [
                    html.Div(
                        [
                            html.H4("40 eV fragmentation similarity", id="fragment-40-similarity-title", className="h4 mb-4 text-gray-800"),
                            html.Div("Cosine similarity", id="fragment-40-cosine-text"),
                            html.Div("", id="fragment-40-similarity-modal"),
                            html.Div("Cosine of root square similarity", id="fragment-40-cosine-root-text", style={'display': 'none'}),
                            html.Div("", id="fragment-40-similarity-cosine-root-modal", style={'display': 'none'}),
                            html.Div("Pearson similarity", id="fragment-40-pearson-text", style={'display': 'none'}),
                            html.Div("", id="fragment-40-similarity-pearson-modal", style={'display': 'none'}),
                            html.Div("Scholle similarity", id="fragment-40-scholle-text"),
                            html.Div("", id="fragment-40-similarity-scholle-modal"),
                        ]
                        ),
                ],width=4),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("profil-isotopique-theorique-modal", "Profil Isotopique Théorique"),
                ],width=5),
                dbc.Col(
                    [
                    cc.ChartCard("profil-isotopique-experimental-modal", "Profil Isotopique Expérimental"),
                ],width=5),
                dbc.Col(
                    [
                    html.Div(
                        [
                            html.H4("Isotopic profiles similarity", id="isotopic-similarity-title", className="h4 mb-4 text-gray-800"),
                            html.Div("", id="isotopic-similarity-modal"),
                        ]
                        ),
                ],width=2),
            ]
        ),
    ])


layout = html.Div(
    [




        html.H1('Résultats'),
        dbc.Row([
                dbc.Col([
                html.Div(id='output-container-range-slider', style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
                dcc.RangeSlider(
                    id='my-range-slider',
                    min=0,
                    max=1,
                    step=0.01,
                    value=[0.9, 1]
                ),
                # html.Br(),
                ], width=3),
                dbc.Col([
                html.Div(id='output-container-id_analysis', children='ID Analyse', style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
                dcc.Dropdown(
                    id='analysis-dropdown',
                    # options=[{'label':name, 'value':name} for name in names]
                    # ,value = 'POS/21-04-20-Mix_14_Med_allion_50_pos-1.mzML'
                    ),
                ], width=3),
                dbc.Col([
                html.Div(id='output-container-mzml-file', children='MZML file', style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
                dcc.Dropdown(
                    id='file-dropdown',
                    # options=[{'label':name, 'value':name} for name in names]
                    # ,value = 'POS/21-04-20-Mix_14_Med_allion_50_pos-1.mzML'
                    ),
                html.P(id='file'),
                ], width=3),
                dbc.Col([
                html.Div(id='output-container-source-bdd', children='Source BDD', style = {'width': '100%', 'display': 'flex', 'align-items': 'center', 'justify-content': 'center'}),
                dcc.Dropdown(
                    id='source-bdd',
                    # options=[{'label':name, 'value':name} for name in names]
                    # ,value = 'POS/21-04-20-Mix_14_Med_allion_50_pos-1.mzML'
                    ),
                ], width=3),
                ]),
        html.Br(),
        daq.BooleanSwitch(
          id='booleanswitch-dash',
          label='Masquer les substances statuées',
          on=True
        ),
        dbc.Row([
            dbc.Col([
            # html.Div([
                dash_table.DataTable(
                    id='table-echantillon-resultat',
                    style_cell={
                        'whiteSpace': 'normal',
                        'overflow': 'hidden',
                        'textOverflow': 'ellipsis',
                        # 'maxWidth': 0,
                        'minWidth': '100px', 
                        # 'width': '140px', 
                        'maxWidth': '140px',
                        # 'minWidth': 95, 'maxWidth': 95, 'width': 95
                        # 'height': 'auto',
                    },
                    # style_cell={
                    #     'minWidth': 95, 'maxWidth': 95, 'width': 95
                    # },
                    style_data_conditional=[
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        },
                        {
                            'if': {'column_editable': True},
                            'backgroundColor': 'rgb(230, 230, 230)'
                        },
                        {
                            'if': {'column_id': 'retention_time_exp'},
                            'display': 'None'
                        },
                        {
                            'if': {'column_id': 'id_analysis'},
                            'display': 'None'
                        },
                        {
                            'if': {'column_id': 'id_mzml'},
                            'display': 'None'
                        },
                        {
                            'if': {'column_id': 'id_molecule'},
                            'display': 'None'
                        },
                    ],
                    style_header_conditional=[
                        {
                            'if': {'column_id': 'retention_time_exp'},
                            'display': 'None'
                        },
                        {
                            'if': {'column_id': 'id_analysis'},
                            'display': 'None'
                        },
                        {
                            'if': {'column_id': 'id_mzml'},
                            'display': 'None'
                        },
                        {
                            'if': {'column_id': 'id_molecule'},
                            'display': 'None'
                        },
                    ],
                    style_filter_conditional=[
                        {
                            'if': {'column_id': 'retention_time_exp'},
                            'display': 'None'
                        },
                        {
                            'if': {'column_id': 'id_analysis'},
                            'display': 'None'
                        },
                        {
                            'if': {'column_id': 'id_mzml'},
                            'display': 'None'
                        },
                        {
                            'if': {'column_id': 'id_molecule'},
                            'display': 'None'
                        },
                    ],
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    },
                    # style_cell={
                    #     'height': 'auto',
                    #     # all three widths are needed
                    #     'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                    #     'whiteSpace': 'normal'
                    # },
                    # # fixed_columns={'headers': True, 'data': 1},
                    # fixed_columns={'headers': True, 'data': 1},
                    style_table={'overflowX': 'auto', 
                    'minWidth': '100%', 
                    # 'overflowY': 'scroll', 
                    'height': 600},
                    fixed_rows={'headers': True},
                    # style_table={'height': 400},
                    # style_table={'maxWidth' : '1500px'},
                    # style_table={'overflowX': 'scroll'},
                    # style_table={'minWidth': '100%'},
                    columns=[{'name': 'Charging ...', 'id': 'Charging ...'}],
                    filter_action="native",
                    sort_action="native",
                    sort_mode="multi",
                    selected_rows=[],
                    # page_action="native",
                    # page_size= 9,
                    export_format='xlsx',
                    export_headers='display',
                    css=[{'selector': '.row', 'rule': 'margin: 0'}],
                ),
            ], width=12, 
            style={'display': 'block', 'margin':'0'}),
            # style={'width': '100%', 
            #      'height': '200px', 
            #      # 'overflow': 'scroll', 
            #      'padding': '10px 10px 10px 20px'
            # }
            # ], style={'display': 'block', 'margin':'0'}),
            ]),


        html.Br(),
        # html.Br(),
        # html.Br(),
        # html.Br(),

        dbc.Row([
                dbc.Col([
                    html.Button(
                        'Montrer les profils',
                        id='show-results',
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
                ], width=4),
                dbc.Col([
                    html.Button(
                        'Appliquer le niveau sur toute la selection du tableau',
                        id='apply-lvl',
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
                    html.Div(children=[
                        dcc.Dropdown(
                            id='lvl-dropdown',
                            options=[{'label':lvl, 'value':lvl} for lvl in lvls]
                            # ,value = 'POS/21-04-20-Mix_14_Med_allion_50_pos-1.mzML'
                        ),
                        ], style = {
                        'width': '100%', 
                        # 'display': 'flex', 
                        'align-items': 'center', 
                        'justify-content': 'center'
                        }),
                ], width=4),
                dbc.Col([
                    html.Button(
                        'Stocker niveau de confiance en BDD',
                        id='store-results',
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
                ], width=4),
                ]),
        html.Div([
                dbc.Modal(
                    [
                        dbc.ModalHeader(html.H1(id="modal-header", children="")),
                        dbc.ModalBody(html.Div(modal_layout)),
                        # dbc.ModalFooter([
                        #     html.Div(id='testp', children=''),
                        #     dbc.Button("Close", id="close", className="ml-auto")
                        # ]),
                    ],
                    id="modal",
                    size="xl",
                ),
            ]),


        # dbc.Row(
        #     [
        #         dbc.Col(
        #             [
        #                 html.Div(id='buttons-echantillon-resultat', children=[
        #                     html.P('button')
        #                 ]),

        #                 html.Div(id='output-data-upload-resultat'),
        #         ],width=6),
        #         dbc.Col(
        #             [
        #                 html.Div(id='buttons-launch-analysis-resultat', children=[
        #                     html.Button(
        #                         'Lancer analyse',
        #                         id='launch-analysis-resultat',
        #                         style={
        #                             'width': '100%',
        #                             'height': '60px',
        #                             'lineHeight': '60px',
        #                             'borderWidth': '1px',
        #                             'borderRadius': '5px',
        #                             'textAlign': 'center',
        #                             'margin': '10px'
        #                         },
        #                     ),

        #                     dbc.Row([
        #                         dbc.Col([
        #                             html.Label('Threshold positif'),
        #                             dcc.Input(id='threshold-positif-resultat', value=10000),
        #                         ],width=4),
        #                         dbc.Col([
        #                             html.Label('Threshold negatif'),
        #                             dcc.Input(id='threshold-negatif-resultat', value=1000),
        #                         ],width=4),
        #                         dbc.Col([
        #                             html.Label('Base de données'),
        #                             dcc.Dropdown(
        #                                 id='molecule-bdd-resultat',
        #                                 options=[],
        #                                 # value=['INERIS', 'Agilent'],
        #                                 multi=True
        #                             )  
        #                         ],width=4),
        #                     ]),

        #                     html.Div(id='selected-row-ids-echantillon-resultat'),
        #                     html.Div(id='selected-row-ids-echantillon-test-resultat'),
        #                     dcc.ConfirmDialog(
        #                         id='confirm-resultat',
        #                         message='Danger danger! Are you sure you want to continue?',
        #                     ),
        #                 ]),

        #         ],width=6)
        #     ]
        # ),

        
        html.Div(id='intermediate-value-echantillon-resultat', style={'display': 'none'}),
        html.Div(id='non-displayed-resultat', style={'display': 'none'})

        ])