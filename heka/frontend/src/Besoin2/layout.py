import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from functools import partial
from Besoin2.helpers import *
import custom_components as cc
import pandas as pd

layout_mode_comparison = html.Div(children=[
    dbc.Row([
        dbc.FormGroup([
            dbc.Label("Mode comparaison"),
            dbc.RadioItems(
                options=[
                    {"label": "1 profil", "value": "1"},
                    {"label": "2 profils", "value": "2"},
                ],
                value="1",
                id="radio_mode",
                inline=True,
            ),
        ])
    ])],
    style={"margin-left": "1%"})

layout_perimeters_1 = html.Div(children=[
    dbc.Row([
        dbc.Col([
            html.P("Projet", style={"text-align" : "center"}),
            dcc.Dropdown(
                id='id_filtre_projet_main',
                placeholder="Projet",
                options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories["projet"].sort_values())],
                style={"min-width" : "100px"},
                multi=True
            )],
            width=3
        ),
        dbc.Col([
            html.P("Distance à la source", style={"text-align" : "center"}),
            dcc.Dropdown(
                id='id_filtre_distance_main',
                placeholder="Distance",
                options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories["distance"].sort_values())],
                style={"min-width" : "100px"},
                multi=True
            )],
            width=3
        ),
        dbc.Col([
            html.P("Matrice", style={"text-align" : "center"}),
            dcc.Dropdown(
                id='id_filtre_matrice_main',
                placeholder="Matrice",
                options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories["matrice"].sort_values())],
                style={"min-width" : "100px"},
                multi=True
            )],
            width=3
        ),
        dbc.Col([
            html.P("Type de mesure", style={"text-align" : "center"}),
            dcc.Dropdown(
                id='id_filtre_mesure_main',
                placeholder="Mesure",
                options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories["mesure"].sort_values())],
                style={"min-width" : "100px"},
                multi=True
            )],
            width=3
        )
            ])],
    id = "perimeters_layout_1"
)

layout_perimeters_2 = html.Div(children=[
        dbc.Row([
            dbc.Col([
                html.H5("Profil 1"),
                dbc.Row([
                    dbc.Col([
                        html.P("Projet", style={"text-align" : "center"}),
                        dcc.Dropdown(
                            id='id_filtre_projet_1',
                            placeholder="Projet",
                            options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories["projet"].sort_values())],
                            style={"min-width" : "100px"},
                            multi=True
                        )],
                        width=3
                    ),
                    dbc.Col([
                        html.P("Distance à la source", style={"text-align" : "center"}),
                        dcc.Dropdown(
                            id='id_filtre_distance_1',
                            placeholder="Distance",
                            options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories["distance"].sort_values())],
                            style={"min-width" : "100px"},
                            multi=True
                        )],
                        width=3
                    ),
                    dbc.Col([
                        html.P("Matrice", style={"text-align" : "center"}),
                        dcc.Dropdown(
                            id='id_filtre_matrice_1',
                            placeholder="Matrice",
                            options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories["matrice"].sort_values())],
                            style={"min-width" : "100px"},
                            multi=True
                        )],
                        width=3
                    ),
                    dbc.Col([
                        html.P("Type de mesure", style={"text-align" : "center"}),
                        dcc.Dropdown(
                            id='id_filtre_mesure_1',
                            placeholder="Mesure",
                            options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories["mesure"].sort_values())],
                            style={"min-width" : "100px"},
                            multi=True
                        )],
                        width=3
                    )
                ])],
            width=6,
            style={"border-right": "1px solid black"}),
            dbc.Col([
                html.H5("Profil 2"),
                dbc.Row([
                    dbc.Col([
                        html.P("Projet", style={"text-align" : "center"}),
                        dcc.Dropdown(
                            id='id_filtre_projet_2',
                            placeholder="Projet",
                            options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories["projet"].sort_values())],
                            style={"min-width" : "100px"},
                            multi=True
                        )],
                        width=3
                    ),
                    dbc.Col([
                        html.P("Distance à la source", style={"text-align" : "center"}),
                        dcc.Dropdown(
                            id='id_filtre_distance_2',
                            placeholder="Distance",
                            options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories["distance"].sort_values())],
                            style={"min-width" : "100px"},
                            multi=True
                        )],
                        width=3
                    ),
                    dbc.Col([
                        html.P("Matrice", style={"text-align" : "center"}),
                        dcc.Dropdown(
                            id='id_filtre_matrice_2',
                            placeholder="Matrice",
                            options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories["matrice"].sort_values())],
                            style={"min-width" : "100px"},
                            multi=True
                        )],
                        width=3
                    ),
                    dbc.Col([
                        html.P("Type de mesure", style={"text-align" : "center"}),
                        dcc.Dropdown(
                            id='id_filtre_mesure_2',
                            placeholder="Mesure",
                            options=[{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories["mesure"].sort_values())],
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

layout_parameter_1 = html.Div(children=[
    dbc.Row([
        dbc.Col([
            html.P("Normalisation", style={"text-align" : "center"}),
            dcc.Dropdown(
                id='id_normalisation_main',
                options=[{'label':"Normalisation A", 'value':"norme_A"}, {'label':"Normalisation C", 'value':"norme_C"}],
                placeholder="Sélectionnez la normalisation"
            )
        ]),
        dbc.Col([
            html.P("Métrique utilisée", style={"text-align" : "center"}),
            dcc.Dropdown(
                id='id_metric_main',
                options=[{'label':"Moyenne", 'value':"mean"},{'label':"Médiane", 'value':"median"}],
                placeholder="Sélectionnez la métrique"
            )
        ]),
        dbc.Col([
            html.P("Variable en ordonnée", style={"text-align" : "center"}),
            dcc.Dropdown(
                id='id_varexp_main',
                options=[
                    {'label':"Distance à la source", 'value':"distance"},
                    {'label':"Matrice", 'value':"matrice"},
                    {'label':"Projet", 'value':"projet"},
                    {'label':"Type de point de mesure", 'value':"mesure"}
                ],
                placeholder="Sélectionnez la variable en ordonnée"
            )
        ])
    ])],
    id = "parameters_layout_1"
)

layout_parameter_2 = html.Div(children=[
    dbc.Row([
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.P("Normalisation", style={"text-align" : "center"}),
                    dcc.Dropdown(
                        id='id_normalisation_1',
                        options=[{'label':"Normalisation A", 'value':"norme_A"}, {'label':"Normalisation C", 'value':"norme_C"}],
                        placeholder="Normalisation"
                    )
                ]),
                dbc.Col([
                    html.P("Métrique utilisée", style={"text-align" : "center"}),
                    dcc.Dropdown(
                        id='id_metric_1',
                        options=[{'label':"Moyenne", 'value':"mean"},{'label':"Médiane", 'value':"median"}],
                        placeholder="Métrique"
                    )
                ]),
                dbc.Col([
                    html.P("Variable en ordonnée", style={"text-align" : "center"}),
                    dcc.Dropdown(
                        id='id_varexp_1',
                        options=[
                            {'label':"Distance à la source", 'value':"distance"},
                            {'label':"Matrice", 'value':"matrice"},
                            {'label':"Projet", 'value':"projet"},
                            {'label':"Type de point de mesure", 'value':"mesure"}
                        ],
                        placeholder="Variable en ordonnée"
                    )
                ])
            ])
        ],
        width=6,
        style={"border-right": "1px solid black"}),
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    html.P("Normalisation", style={"text-align" : "center"}),
                    dcc.Dropdown(
                        id='id_normalisation_2',
                        options=[{'label':"Normalisation A", 'value':"norme_A"}, {'label':"Normalisation C", 'value':"norme_C"}],
                        placeholder="Normalisation"
                    )
                ]),
                dbc.Col([
                    html.P("Métrique utilisée", style={"text-align" : "center"}),
                    dcc.Dropdown(
                        id='id_metric_2',
                        options=[{'label':"Moyenne", 'value':"mean"},{'label':"Médiane", 'value':"median"}],
                        placeholder="Métrique"
                    )
                ]),
                dbc.Col([
                    html.P("Variable en ordonnée", style={"text-align" : "center"}),
                    dcc.Dropdown(
                        id='id_varexp_2',
                        options=[
                            {'label':"Distance à la source", 'value':"distance"},
                            {'label':"Matrice", 'value':"matrice"},
                            {'label':"Projet", 'value':"projet"},
                            {'label':"Type de point de mesure", 'value':"mesure"}
                        ],
                        placeholder="Variable en ordonnée"
                    )
                ])
            ])
        ],
        width=6)
    ])],
    id = "parameters_layout_2"
)

layout_comparaison = html.Div(children=[
        html.P("")
    ],
    id="comparison_layout"
)


layout = html.Div(children=[
    html.H1("Profils des échantillons"),
    html.Br(),
    html.H3("Comparaison"),
    layout_mode_comparison,
    html.Br(),
    html.H3("Périmètre"),
    html.Div(children=[
        layout_perimeters_1],
        id = "layout_perimeters_id"),
    html.Br(),
    html.Br(),
    html.H3("Paramètres"),
    html.Div(children=[
        layout_parameter_1],
        id = "layout_parameters_id"),
    html.Br(),
    html.Br(),
    html.Div(
        children=[html.Button('Générer', id='generate_1')],
        style={"text-align" : "center"},
        id="div_button"),
    html.Br(),
    html.H3("Profil"),
    layout_comparaison,
    html.Br(),
    html.H3("Résultats de similarité (Dot Product)"),
        html.Div(children=[
        dbc.Row([
            dbc.Col([
                html.Div([
                    ],
                    id="dot_cross_table")],
                    width=12)]
        )],
        id = "layout_similarity_id"),
    html.Br(),
    html.H3("Volumétrie"),
    html.Div(children=[
        dbc.Row([
            dbc.Col([
                cc.ChartCard("chart_volume_main", "Volumetrie du profil")],
                width=6)],
                justify="center"
        )],
        id = "layout_volumetrie_id"),

])
