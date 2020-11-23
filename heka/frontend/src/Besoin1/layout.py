import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import custom_components as cc
from Besoin1.helpers import *
import dash_table as dt



blobs = list_blobs()
names = [i['blob_name'].split('/')[-2]+'/'+i['blob_name'].split('/')[-1] for i in blobs if ((i['blob_name'][-4:] == 'mzML') and ("_Med" not in i['blob_name'].split('/')[-1]) and ("Pesticides" not in i['blob_name'].split('/')[-1]) and ("mix_perfluores" not in i['blob_name'].split('/')[-1]) and ("bisphenols" not in i['blob_name'].split('/')[-1]))]


df = get_df_full_query("""SELECT molecule_name FROM public.molecules GROUP BY 1 ORDER BY 1;""")
Meds = list(df['molecule_name'].values)



layout = html.Div(
    [
        html.H1('Reading mzML'),
        html.Div([
        dcc.Dropdown(
            id='name-dropdown',
            options=[{'label':name, 'value':name} for name in names]
            # ,value = 'POS/21-04-20-Mix_14_Med_allion_50_pos-1.mzML'
            ),
            ],style={'width': '49.25%', 'display': 'inline-block'}),
        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("chromatogram", "Chromatogram"),
                ],width=8),
                dbc.Col(
                    [
                    html.Br(),
                    html.H4("Spectrum number", id="Nb_spectrum", className="h4 mb-4 text-gray-800"),
                    html.Div("", id="Nb_spectrum_value"),
                    html.Br(),
                    html.H4("Acquistion mode", id="Acq_mode", className="h4 mb-4 text-gray-800"),
                    html.Div("", id="Acq_mode_value"),
                    html.Br(),
                    html.H4("Ionisation mode", id="Ion_mode", className="h4 mb-4 text-gray-800"),
                    html.Div("", id="Ion_mode_value"),
                ],width=4)
            ]
        ),

        html.Hr(),

        html.H1('Choosing the molecule to look for'),
        dbc.Row(
            [
                dbc.Col(
                    [
                    dcc.Dropdown(
                    id='name-dropdown-Mol',
                    options=[{'label':name, 'value':name} for name in Meds]
                    ),                    
                ],width=4),
                dbc.Col(
                    [
                    dcc.Dropdown(
                    id='name-dropdown-Source',
                    options=[]
                    ),                    
                ],width=4),
                dbc.Col(
                    [
                    dcc.Dropdown(
                    id='name-dropdown-Species',
                    options=[]
                    ),                    
                ],width=4),
            ]
        ),


        # html.Div([
        # dcc.Dropdown(
        #     id='name-dropdown-Mol',
        #     options=[{'label':name, 'value':name} for name in Meds]
        #     # ,value = 'Acebutolol'
        #     ),
        #     ],style={'width': '49.25%', 'display': 'inline-block'}),
        dbc.Row(
            [
                dbc.Col(
                    [
                    # cc.ChartCard("profil-isotopique", "Profil Isotopique"),
                    cc.ChartCard("search-in-chromato", "Search on chromatogram"),

                ],width=8),
                dbc.Col(
                    [
                    html.Br(),
                    html.H4("Mass", id="Mass", className="h4 mb-4 text-gray-800"),
                    html.Div("", id="Mass_value"),
                    html.Br(),
                    html.H4("Retention time", id="RT", className="h4 mb-4 text-gray-800"),
                    html.Div("", id="RT_value"),
                    html.Br(),
                    html.H4("Extracted peaks", id="extracted-peaks-title", className="h4 mb-4 text-gray-800"),
                    html.Div(
                                [
                                    dt.DataTable(id='datatable-peaks', 
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
        html.Div([
        dcc.Dropdown(
            id='opt-dropdown-spectrum',
            ),
            ],style={'width': '49.25%', 'display': 'inline-block'}
        ),
        html.Div([],style={'width': '50.75%', 'display': 'inline-block'}),
        # dbc.Row(
        #     [
        #         dbc.Col(
        #             [
        #             # cc.ChartCard("search-in-chromato", "Search on chromatogram"),
        #             cc.ChartCard("scan-spectrum", "Scan"),
        #         ],width=8),
        #         dbc.Col(
        #             [
        #             # cc.ChartCard("scan-spectrum", "Scan"),
        #         ],width=4),
        #     ]
        # ),
        # dbc.Row(
        #     [
        #         dbc.Col(
        #             [
        #             cc.ChartCard("search-fragment-10", "Following fragmentation with 10eV"),
        #         ],width=4),
        #         dbc.Col(
        #             [
        #             cc.ChartCard("search-fragment-20", "Following fragmentation with 20eV"),
        #         ],width=4),
        #         dbc.Col(
        #             [
        #             cc.ChartCard("search-fragment-40", "Following fragmentation with 40eV"),
        #         ],width=4),
        #     ]
        # ),

        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("search-fragment-10-only-fragment", "Fragmentation with 10eV with fragment only"),
                ],width=4),
                dbc.Col(
                    [
                    cc.ChartCard("search-fragment-20-only-fragment", "Fragmentation with 20eV with fragment only"),
                ],width=4),
                dbc.Col(
                    [
                    cc.ChartCard("search-fragment-40-only-fragment", "Fragmentation with 40eV with fragment only"),
                ],width=4),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("fragment-10", "Fragmentation with 10eV of molecule to look for"),
                ],width=4),
                dbc.Col(
                    [
                    cc.ChartCard("fragment-20", "Fragmentation with 20eV of molecule to look for"),
                ],width=4),
                dbc.Col(
                    [
                    cc.ChartCard("fragment-40", "Fragmentation with 40eV of molecule to look for"),
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
                            html.Div("Cosine similarity", id="fragment-10-cosine-text"),
                            html.Div("", id="fragment-10-similarity"),
                            html.Div("Cosine of root square similarity", id="fragment-10-cosine-root-text"),
                            html.Div("", id="fragment-10-similarity-cosine-root"),
                            html.Div("Pearson similarity", id="fragment-10-pearson-text"),
                            html.Div("", id="fragment-10-similarity-pearson"),
                            html.Div("Scholle similarity", id="fragment-10-scholle-text"),
                            html.Div("", id="fragment-10-similarity-scholle"),                            
                        ]
                        ),
                ],width=4),
                dbc.Col(
                    [
                    html.Div(
                        [
                            html.H4("20 eV fragmentation similarity", id="fragment-20-similarity-title", className="h4 mb-4 text-gray-800"),
                            html.Div("Cosine similarity", id="fragment-20-cosine-text"),
                            html.Div("", id="fragment-20-similarity"),
                            html.Div("Cosine of root square similarity", id="fragment-20-cosine-root-text"),
                            html.Div("", id="fragment-20-similarity-cosine-root"),
                            html.Div("Pearson similarity", id="fragment-20-pearson-text"),
                            html.Div("", id="fragment-20-similarity-pearson"),
                            html.Div("Scholle similarity", id="fragment-20-scholle-text"),
                            html.Div("", id="fragment-20-similarity-scholle"),                    
                        ]
                        ),
                ],width=4),
                dbc.Col(
                    [
                    html.Div(
                        [
                            html.H4("40 eV fragmentation similarity", id="fragment-40-similarity-title", className="h4 mb-4 text-gray-800"),
                            html.Div("Cosine similarity", id="fragment-40-cosine-text"),
                            html.Div("", id="fragment-40-similarity"),
                            html.Div("Cosine of root square similarity", id="fragment-40-cosine-root-text"),
                            html.Div("", id="fragment-40-similarity-cosine-root"),
                            html.Div("Pearson similarity", id="fragment-40-pearson-text"),
                            html.Div("", id="fragment-40-similarity-pearson"),
                            html.Div("Scholle similarity", id="fragment-40-scholle-text"),
                            html.Div("", id="fragment-40-similarity-scholle"),
                        ]
                        ),
                ],width=4),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                    cc.ChartCard("profil-isotopique-theorique", "Profil Isotopique Théorique"),
                ],width=5),
                dbc.Col(
                    [
                    cc.ChartCard("profil-isotopique-experimental", "Profil Isotopique Expérimental"),
                ],width=5),
                dbc.Col(
                    [
                    html.Div(
                        [
                            html.H4("Isotopic profiles similarity", id="isotopic-similarity-title", className="h4 mb-4 text-gray-800"),
                            html.Div("", id="isotopic-similarity"),
                        ]
                        ),
                ],width=2),
            ]
        ),

        ])