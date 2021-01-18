import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from functools import partial
import custom_components as cc
import pandas as pd
import dash_table
import Besoin2_final.helpers as hp

layout_perimeters = html.Div(children=[
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.P("Projet", style={"text-align" : "center"}),
                    dcc.Dropdown(
                        id='id_filtre_projet',
                        placeholder="Projet",
                        options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(hp.df_categories_final["projet"].sort_values())],
                        style={"min-width" : "100px"},
                        multi=True
                    )],
                    width=3
                ),
                dbc.Col([
                    html.P("Distance à la source", style={"text-align" : "center"}),
                    dcc.Dropdown(
                        id='id_filtre_distance',
                        placeholder="Distance",
                        options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(hp.df_categories_final["distance"].sort_values())],
                        style={"min-width" : "100px"},
                        multi=True
                    )],
                    width=3
                ),
                dbc.Col([
                    html.P("Matrice", style={"text-align" : "center"}),
                    dcc.Dropdown(
                        id='id_filtre_matrice',
                        placeholder="Matrice",
                        options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(hp.df_categories_final["matrice"].sort_values())],
                        style={"min-width" : "100px"},
                        multi=True
                    )],
                    width=3
                ),
                dbc.Col([
                    html.P("Type de mesure", style={"text-align" : "center"}),
                    dcc.Dropdown(
                        id='id_filtre_mesure',
                        placeholder="Mesure",
                        options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(hp.df_categories_final["mesure"].sort_values())],
                        style={"min-width" : "100px"},
                        multi=True
                    )],
                    width=3
                )
            ])],
            width = 11
        ),
        dbc.Col([
            html.Br(),
            dbc.Button("Analyse", id="analyse_2")],
            width=1
        )
        ])],
    id = "perimeters_layout"
)

layout_filters = dbc.Row([
    dbc.Col([
        dbc.Row([
            dbc.Col([
                html.P("Métrique utilisée", style={"text-align" : "center"}),
                dcc.Dropdown(
                    id='id_metric',
                    options=[{'label':"Moyenne", 'value':"mean"},{'label':"Médiane", 'value':"median"}],
                    placeholder="Métrique"
                )
            ],
            width = 3),
            dbc.Col([
                html.P("Normalisation", style={"text-align" : "center"}),
                dcc.Dropdown(
                    id='id_normalisation',
                    options=[{'label':"Normalisation A", 'value':"norme_A"}, {'label':"Normalisation C", 'value':"norme_C"}],
                    placeholder="Normalisation"
                )
            ],
            width = 3)],
            justify="center")],
    width=12)
])

layout_perimeters_2 = html.Div(children=[
        dbc.Row([
            dbc.Col([
                html.H5("Définition du référent"),
                html.P("A l'aide des filtres ci-dessous, des échantillons sont sélectionnés et ensuite aggrégés (selon la métrique choisie précédemment) pour former un unique profil de référence."),
                dbc.Row([
                    dbc.Col([
                        html.P("Projet", style={"text-align" : "center"}),
                        dcc.Dropdown(
                            id='id_filtre_projet_1_bis',
                            placeholder="Projet",
                            options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(hp.df_categories_final["projet"].sort_values())],
                            style={"min-width" : "100px"},
                            multi=True
                        )],
                        width=3
                    ),
                    dbc.Col([
                        html.P("Distance à la source", style={"text-align" : "center"}),
                        dcc.Dropdown(
                            id='id_filtre_distance_1_bis',
                            placeholder="Distance",
                            options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(hp.df_categories_final["distance"].sort_values())],
                            style={"min-width" : "100px"},
                            multi=True
                        )],
                        width=3
                    ),
                    dbc.Col([
                        html.P("Matrice", style={"text-align" : "center"}),
                        dcc.Dropdown(
                            id='id_filtre_matrice_1_bis',
                            placeholder="Matrice",
                            options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(hp.df_categories_final["matrice"].sort_values())],
                            style={"min-width" : "100px"},
                            multi=True
                        )],
                        width=3
                    ),
                    dbc.Col([
                        html.P("Type de mesure", style={"text-align" : "center"}),
                        dcc.Dropdown(
                            id='id_filtre_mesure_1_bis',
                            placeholder="Mesure",
                            options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(hp.df_categories_final["mesure"].sort_values())],
                            style={"min-width" : "100px"},
                            multi=True
                        )],
                        width=3
                    )
                ])],
            width=6,
            style={"border-right": "1px solid black"}),
            dbc.Col([
                html.H5("Définition des comparants"),
                html.P("Les filtres ci-dessous permettent de définir un ensemble d'échantillons de la base de données. Ils sont comparés, à travers le score de similarité, avec le profil sélectionné dans la \"Base de données\"."),
                dbc.Row([
                    dbc.Col([
                        html.P("Projet", style={"text-align" : "center"}),
                        dcc.Dropdown(
                            id='id_filtre_projet_2_bis',
                            placeholder="Projet",
                            options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(hp.df_categories_final["projet"].sort_values())],
                            style={"min-width" : "100px"},
                            multi=True
                        )],
                        width=3
                    ),
                    dbc.Col([
                        html.P("Distance à la source", style={"text-align" : "center"}),
                        dcc.Dropdown(
                            id='id_filtre_distance_2_bis',
                            placeholder="Distance",
                            options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(hp.df_categories_final["distance"].sort_values())],
                            style={"min-width" : "100px"},
                            multi=True
                        )],
                        width=3
                    ),
                    dbc.Col([
                        html.P("Matrice", style={"text-align" : "center"}),
                        dcc.Dropdown(
                            id='id_filtre_matrice_2_bis',
                            placeholder="Matrice",
                            options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(hp.df_categories_final["matrice"].sort_values())],
                            style={"min-width" : "100px"},
                            multi=True
                        )],
                        width=3
                    ),
                    dbc.Col([
                        html.P("Type de mesure", style={"text-align" : "center"}),
                        dcc.Dropdown(
                            id='id_filtre_mesure_2_bis',
                            placeholder="Mesure",
                            options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(hp.df_categories_final["mesure"].sort_values())],
                            style={"min-width" : "100px"},
                            multi=True
                        )],
                        width=3
                    )
                ])],
            width=6)
        ])
    ],
    id="perimeters_layout_2"
)

layout_db = html.Div(
    [
        dbc.Row([
            dbc.Col([
                dbc.Button(
                    "Importer les échantillons",
                    id="collapse-button",
                    className="mb-3"
                )],
            width = 2),
            dbc.Col([
                dcc.Link(
                    dbc.Button(
                        "Télécharger les échantillons",
                        id="download",
                        className="mb-3"
                    ),
                    href="/ineris/api/c13s/get_db",
                    refresh=True
                )],
            width = 2),
            dbc.Col([
                dcc.Link(
                    dbc.Button(
                        "Télécharger les données initiales",
                        id="download_init",
                        className="mb-3"
                    ),
                    href="/ineris/api/c13s/get_db_init",
                    refresh=True
                )],
            width = 3)
        ]),
        dbc.Collapse(
            html.Div(id='buttons-echantillon', children=[
                html.Div(id="warning_type_file"),
                dcc.Upload(
                    id='upload_data_echantillon',
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
                    }
                ),
            ]),
            id="collapse",
        ),
    ]
)

layout = html.Div(children=[
    dcc.Interval(id='refresh', interval=100, max_intervals=100),
    html.H2("Base de données"),
    html.P("Cette partie gère l'import et l'export des échantillons à la base de données. Pour la suite des analyses, il est nécessaire de sélectionner les échantillons et les paramètres des analyses (métrique et normalisation)."),
    html.Br(),
    layout_db,
    html.Br(),
    dcc.Loading(
        id="loading-0",
        type="default",
        children = dash_table.DataTable(
            id='table_db',
            columns=[{'name': i, 'id': i} for i in hp.df[hp.columns_ind + hp.substances].columns],
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            selected_rows=[],
            page_action="native",
            page_size= 10,
            style_table={'overflowX': 'auto'},
            row_selectable='multi',
            css=[{'selector': '.row', 'rule': 'margin: 0'}],
            data=hp.df[hp.columns_ind + hp.substances].to_dict('records')
        )
    ),
    html.Br(),
    layout_filters,
    html.Br(),
    html.H2("Profils"),
    html.P("Cette partie génère les profils des échantillons sélectionnés avec la normalisation et la métrique choisies."),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dbc.Button(
                "Génération des profils",
                id="analyse")],
            width = 3)],
            justify="center"
    ),
    html.Br(),
    html.Div(id="warning"),
    dcc.Loading(
        id="loading-1",
        type="default",
        children = dash_table.DataTable(
            id='table_db_profil',
            columns=[{'name': 'Charging ...', 'id': 'Charging ...'}],
            filter_action="native",
            sort_action="native",
            sort_mode="multi",
            selected_rows=[],
            page_action="native",
            page_size= 10,
            style_table={'overflowX': 'auto'},
            row_selectable='single',
            css=[{'selector': '.row', 'rule': 'margin: 0'}]
        )
    ),
    html.Br(),
    html.H2("Résultats de comparaison"),
    html.P("Dans cette partie, la plateforme recherche les échantillons dont le score de similarité (Cosine Similarity) est le plus élevé avec les échantillons sélectionnés dans la partie \"Base de données\". Il est nécessaire de définir la métrique et la normalisation pour que la recherche fonctionne. Par ailleurs, avec les filtres (facultatifs) ci-dessous, il est possible de définir le périmètre de la recherche."),
    html.Br(),
    layout_perimeters,
    html.Br(),
    html.H5("Scores de similarités"),
    html.Br(),
    dcc.Loading(
        id="loading-2",
        type="default",
        children = dash_table.DataTable(
            id='table_db_compare',
            columns=[{'name': 'Charging ...', 'id': 'Charging ...'}],
            sort_action="native",
            sort_mode="multi",
            selected_rows=[],
            page_action="native",
            page_size= 10,
            style_table={'overflowX': 'auto'},
            css=[{'selector': '.row', 'rule': 'margin: 0'}]
        )
    ),
    html.Br(),
    html.H5("Profils des échantillons les plus proches"),
    dcc.Loading(
        id="loading-3",
        type="default",
        children = dash_table.DataTable(
            id='table_profils', 
            sort_action="native",
            columns=[{'name': 'Charging ...', 'id': 'Charging ...'}],
            style_table={'overflowX': 'auto'},
            style_cell={
                'height': 'auto',
                'minWidth': '50px', 'width': '20px', 'maxWidth': '100px',
                'whiteSpace': 'normal'
            },
            css=[{'selector': '.row', 'rule': 'margin: 0'}]
        )),
    html.Br(),
    html.H2("Impact de la source"),
    html.P("Le fonctionnement de la partie \"Impact de la source\" se décompose en 2 partie : "),
    html.Ul(
        id='my-list',
        children=[
            html.Li("Dans un premier temps, la plateforme affiche la distribution du score de similarité (Cosine Similarity) des profils des 'Comparants' avec celui du 'Référent'. En d'autres termes, pour chaque profil dans les 'Comparants', un score de similarité est calculé à l'aide du profil 'Référent'."),
            html.Li("Dans un second temps, le score de similarité entre le profil 'Référent' et celui selectionné dans la partie \"Base de données\" est calculé. Il est ensuite affiché direcement sur la distribution des scores de similarité des 'Comparants'.")]
    ),
    html.Br(),
    layout_perimeters_2,
    html.Br(),
    dbc.Row([
        dbc.Button("Analyse de l'impact", id="analyse_3")],
        justify="center"
    ),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Loading(
                id="loading-3",
                type="default",
                children=cc.ChartCard("chart_resultat", "Impact"))],
            width=9)],
        justify="center"
    )
])