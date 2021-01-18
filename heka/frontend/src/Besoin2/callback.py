import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import dash_html_components as html
import json
import os
from Besoin2.helpers import *
from Besoin2.layout import *
import numpy as np
import dash_table
import pandas as pd
import custom_components as cc


def register_callbacks(app):
    ## Gestion du radio boutton qui permet de changer le mode de comparaison
    @app.callback(
        [dash.dependencies.Output('layout_perimeters_id', 'children'),
        dash.dependencies.Output('layout_parameters_id', 'children'),
        dash.dependencies.Output('div_button', 'children'),
        dash.dependencies.Output('comparison_layout', 'children'),
        dash.dependencies.Output('layout_volumetrie_id', 'children'),
        dash.dependencies.Output('layout_similarity_id', 'children')],
        [dash.dependencies.Input('radio_mode', 'value')]
    )
    def choose_mode(mode):
        if(mode == "1"):
            return (layout_perimeters_1,
            layout_parameter_1,
            html.Button('Générer', id='generate_1'),
            html.Div(children=[html.P("")], id="comparison_layout_1"),
            dbc.Row([
                dbc.Col([
                    cc.ChartCard("chart_volume_main", "Volumetrie du profil")],
                    width=6)],
                justify="center"
            ),
            dbc.Row([
                dbc.Col([
                    html.Div([html.P(" ")], id="dot_cross_table")],
                    width=12)],
                justify="center"
            )
        )
        elif(mode == "2"):
            return (layout_perimeters_2,
            layout_parameter_2,
            html.Button('Générer', id='generate_2'),
            html.Div(children=[html.P("")], id="comparison_layout_2"),
            dbc.Row([
                dbc.Col([
                    cc.ChartCard("chart_volume_1", "Volumetrie du profil 1")],
                    width=6),
                dbc.Col([
                    cc.ChartCard("chart_volume_2", "Volumetrie du profil 2")],
                    width=6)
            ]),
            dbc.Row([
                dbc.Col([
                    html.Div([html.P(" ")], id="dot_cross_table_1")],
                    width=6),
                dbc.Col([
                    html.Div([html.P(" ")], id="dot_cross_table_2")],
                    width=6)
            ])
        )

    ## Gestion du filtre projet
    @app.callback(
        dash.dependencies.Output('id_filtre_projet_main', 'options'),
        [dash.dependencies.Input('id_filtre_distance_main', 'value'),
        dash.dependencies.Input('id_filtre_matrice_main', 'value'),
        dash.dependencies.Input('id_filtre_mesure_main', 'value')]
    )
    def filter_dynamic_projet(value_distance, value_matrice, value_mesure):
        df_categories_filter = df_categories.copy()
        
        if(value_distance != None and value_distance != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["distance"].isin(value_distance))]

        if(value_matrice != None and value_matrice != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["matrice"].isin(value_matrice))]

        if(value_mesure != None and value_mesure != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["mesure"].isin(value_mesure))]

        return [{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories_filter["projet"].sort_values())]

    ## Gestion du filtre distance
    @app.callback(
        dash.dependencies.Output('id_filtre_distance_main', 'options'),
        [dash.dependencies.Input('id_filtre_projet_main', 'value'),
        dash.dependencies.Input('id_filtre_matrice_main', 'value'),
        dash.dependencies.Input('id_filtre_mesure_main', 'value')]
    )
    def filter_dynamic_distance(value_projet, value_matrice, value_mesure):
        df_categories_filter = df_categories.copy()
        
        if(value_projet != None and value_projet != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["projet"].isin(value_projet))]

        if(value_matrice != None and value_matrice != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["matrice"].isin(value_matrice))]

        if(value_mesure != None and value_mesure != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["mesure"].isin(value_mesure))]

        return [{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories_filter["distance"].sort_values())]


    ## Gestion du filtre matrice
    @app.callback(
        dash.dependencies.Output('id_filtre_matrice_main', 'options'),
        [dash.dependencies.Input('id_filtre_distance_main', 'value'),
        dash.dependencies.Input('id_filtre_projet_main', 'value'),
        dash.dependencies.Input('id_filtre_mesure_main', 'value')]
    )
    def filter_dynamic_matrice(value_distance, value_projet, value_mesure):
        df_categories_filter = df_categories.copy()
        
        if(value_distance != None and value_distance != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["distance"].isin(value_distance))]

        if(value_projet != None and value_projet != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["projet"].isin(value_projet))]

        if(value_mesure != None and value_mesure != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["mesure"].isin(value_mesure))]

        return [{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories_filter["matrice"].sort_values())]

    
    ## Gestion du filtre mesure
    @app.callback(
        dash.dependencies.Output('id_filtre_mesure_main', 'options'),
        [dash.dependencies.Input('id_filtre_distance_main', 'value'),
        dash.dependencies.Input('id_filtre_matrice_main', 'value'),
        dash.dependencies.Input('id_filtre_projet_main', 'value')]
    )
    def filter_dynamic_mesure(value_distance, value_matrice, value_projet):
        df_categories_filter = df_categories.copy()
        
        if(value_distance != None and value_distance != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["distance"].isin(value_distance))]

        if(value_matrice != None and value_matrice != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["matrice"].isin(value_matrice))]

        if(value_projet != None and value_projet != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["projet"].isin(value_projet))]

        return [{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories_filter["mesure"].sort_values())]


    ## Gestion du filtre projet
    @app.callback(
        [dash.dependencies.Output('id_filtre_projet_1', 'options'),
        dash.dependencies.Output('id_filtre_projet_2', 'options')],
        [dash.dependencies.Input('id_filtre_distance_1', 'value'),
        dash.dependencies.Input('id_filtre_matrice_1', 'value'),
        dash.dependencies.Input('id_filtre_mesure_1', 'value'),
        dash.dependencies.Input('id_filtre_distance_2', 'value'),
        dash.dependencies.Input('id_filtre_matrice_2', 'value'),
        dash.dependencies.Input('id_filtre_mesure_2', 'value')]
    )
    def filter_dynamic_projet_compare(value_distance_1, value_matrice_1, value_mesure_1, value_distance_2, value_matrice_2, value_mesure_2):
        df_categories_filter_1 = df_categories.copy()
        df_categories_filter_2 = df_categories.copy()
        
        if(value_distance_1 != None and value_distance_1 != []):
            df_categories_filter_1 = df_categories_filter_1[(df_categories_filter_1["distance"].isin(value_distance_1))]

        if(value_matrice_1 != None and value_matrice_1 != []):
            df_categories_filter_1 = df_categories_filter_1[(df_categories_filter_1["matrice"].isin(value_matrice_1))]

        if(value_mesure_1 != None and value_mesure_1 != []):
            df_categories_filter_1 = df_categories_filter_1[(df_categories_filter_1["mesure"].isin(value_mesure_1))]

        if(value_distance_2 != None and value_distance_2 != []):
            df_categories_filter_2 = df_categories_filter_2[(df_categories_filter_2["distance"].isin(value_distance_2))]

        if(value_matrice_2 != None and value_matrice_2 != []):
            df_categories_filter_2 = df_categories_filter_2[(df_categories_filter_2["matrice"].isin(value_matrice_2))]

        if(value_mesure_2 != None and value_mesure_2 != []):
            df_categories_filter_2 = df_categories_filter_2[(df_categories_filter_2["mesure"].isin(value_mesure_2))]

        return ([{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories_filter_1["projet"].sort_values())],
            [{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories_filter_2["projet"].sort_values())])

    ## Gestion du filtre distance
    @app.callback(
        [dash.dependencies.Output('id_filtre_distance_1', 'options'),
        dash.dependencies.Output('id_filtre_distance_2', 'options')],
        [dash.dependencies.Input('id_filtre_projet_1', 'value'),
        dash.dependencies.Input('id_filtre_matrice_1', 'value'),
        dash.dependencies.Input('id_filtre_mesure_1', 'value'),
        dash.dependencies.Input('id_filtre_projet_2', 'value'),
        dash.dependencies.Input('id_filtre_matrice_2', 'value'),
        dash.dependencies.Input('id_filtre_mesure_2', 'value')]
    )
    def filter_dynamic_distance_compare(value_projet_1, value_matrice_1, value_mesure_1, value_projet_2, value_matrice_2, value_mesure_2):
        df_categories_filter_1 = df_categories.copy()
        df_categories_filter_2 = df_categories.copy()
        
        if(value_projet_1 != None and value_projet_1 != []):
            df_categories_filter_1 = df_categories_filter_1[(df_categories_filter_1["projet"].isin(value_projet_1))]

        if(value_matrice_1 != None and value_matrice_1 != []):
            df_categories_filter_1 = df_categories_filter_1[(df_categories_filter_1["matrice"].isin(value_matrice_1))]

        if(value_mesure_1 != None and value_mesure_1 != []):
            df_categories_filter_1 = df_categories_filter_1[(df_categories_filter_1["mesure"].isin(value_mesure_1))]

        if(value_projet_2 != None and value_projet_2 != []):
            df_categories_filter_2 = df_categories_filter_2[(df_categories_filter_2["projet"].isin(value_projet_2))]

        if(value_matrice_2 != None and value_matrice_2 != []):
            df_categories_filter_2 = df_categories_filter_2[(df_categories_filter_2["matrice"].isin(value_matrice_2))]

        if(value_mesure_2 != None and value_mesure_2 != []):
            df_categories_filter_2 = df_categories_filter_2[(df_categories_filter_2["mesure"].isin(value_mesure_2))]

        return ([{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories_filter_1["distance"].sort_values())],
            [{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories_filter_2["distance"].sort_values())])


    ## Gestion du filtre matrice
    @app.callback(
        [dash.dependencies.Output('id_filtre_matrice_1', 'options'),
        dash.dependencies.Output('id_filtre_matrice_2', 'options')],
        [dash.dependencies.Input('id_filtre_distance_1', 'value'),
        dash.dependencies.Input('id_filtre_projet_1', 'value'),
        dash.dependencies.Input('id_filtre_mesure_1', 'value'),
        dash.dependencies.Input('id_filtre_distance_2', 'value'),
        dash.dependencies.Input('id_filtre_projet_2', 'value'),
        dash.dependencies.Input('id_filtre_mesure_2', 'value')]
    )
    def filter_dynamic_matrice_compare(value_distance_1, value_projet_1, value_mesure_1, value_distance_2, value_projet_2, value_mesure_2):
        df_categories_filter_1 = df_categories.copy()
        df_categories_filter_2 = df_categories.copy()
        
        if(value_distance_1 != None and value_distance_1 != []):
            df_categories_filter_1 = df_categories_filter_1[(df_categories_filter_1["distance"].isin(value_distance_1))]

        if(value_projet_1 != None and value_projet_1 != []):
            df_categories_filter_1 = df_categories_filter_1[(df_categories_filter_1["projet"].isin(value_projet_1))]

        if(value_mesure_1 != None and value_mesure_1 != []):
            df_categories_filter_1 = df_categories_filter_1[(df_categories_filter_1["mesure"].isin(value_mesure_1))]

        if(value_distance_2 != None and value_distance_2 != []):
            df_categories_filter_2 = df_categories_filter_2[(df_categories_filter_2["distance"].isin(value_distance_2))]

        if(value_projet_2 != None and value_projet_2 != []):
            df_categories_filter_2 = df_categories_filter_2[(df_categories_filter_2["projet"].isin(value_projet_2))]

        if(value_mesure_2 != None and value_mesure_2 != []):
            df_categories_filter_2 = df_categories_filter_2[(df_categories_filter_2["mesure"].isin(value_mesure_2))]

        return ([{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories_filter_1["matrice"].sort_values())],
            [{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories_filter_2["matrice"].sort_values())])

    ## Gestion du filtre mesure
    @app.callback(
        [dash.dependencies.Output('id_filtre_mesure_1', 'options'),
        dash.dependencies.Output('id_filtre_mesure_2', 'options')],
        [dash.dependencies.Input('id_filtre_distance_1', 'value'),
        dash.dependencies.Input('id_filtre_matrice_1', 'value'),
        dash.dependencies.Input('id_filtre_projet_1', 'value'),
        dash.dependencies.Input('id_filtre_distance_2', 'value'),
        dash.dependencies.Input('id_filtre_matrice_2', 'value'),
        dash.dependencies.Input('id_filtre_projet_2', 'value')]
    )
    def filter_dynamic_mesure(value_distance_1, value_matrice_1, value_projet_1, value_distance_2, value_matrice_2, value_projet_2):
        df_categories_filter_1 = df_categories.copy()
        df_categories_filter_2 = df_categories.copy()
        
        if(value_distance_1 != None and value_distance_1 != []):
            df_categories_filter_1 = df_categories_filter_1[(df_categories_filter_1["distance"].isin(value_distance_1))]

        if(value_matrice_1 != None and value_matrice_1 != []):
            df_categories_filter_1 = df_categories_filter_1[(df_categories_filter_1["matrice"].isin(value_matrice_1))]

        if(value_projet_1 != None and value_projet_1 != []):
            df_categories_filter_1 = df_categories_filter_1[(df_categories_filter_1["projet"].isin(value_projet_1))]

        if(value_distance_2 != None and value_distance_2 != []):
            df_categories_filter_2 = df_categories_filter_2[(df_categories_filter_2["distance"].isin(value_distance_2))]

        if(value_matrice_2 != None and value_matrice_2 != []):
            df_categories_filter_2 = df_categories_filter_2[(df_categories_filter_2["matrice"].isin(value_matrice_2))]

        if(value_projet_2 != None and value_projet_2 != []):
            df_categories_filter_2 = df_categories_filter_2[(df_categories_filter_2["projet"].isin(value_projet_2))]

        return ([{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories_filter_1["mesure"].sort_values())],
            [{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories_filter_2["mesure"].sort_values())])

    ## Gestion du bouton générer pour le mode 2 profils
    @app.callback(
        [dash.dependencies.Output('comparison_layout_2', 'children'),
        dash.dependencies.Output('chart_volume_1', 'figure'),
        dash.dependencies.Output('chart_volume_2', 'figure'),
        dash.dependencies.Output('dot_cross_table_1', 'children'),
        dash.dependencies.Output('dot_cross_table_2', 'children')],
        [dash.dependencies.Input('generate_2', 'n_clicks')],
        [dash.dependencies.State('radio_mode', 'value'),
        dash.dependencies.State('id_filtre_distance_1', 'value'),
        dash.dependencies.State('id_filtre_matrice_1', 'value'),
        dash.dependencies.State('id_filtre_projet_1', 'value'),
        dash.dependencies.State('id_filtre_mesure_1', 'value'),
        dash.dependencies.State('id_normalisation_1', 'value'),
        dash.dependencies.State('id_metric_1', 'value'),
        dash.dependencies.State('id_varexp_1', 'value'),
        dash.dependencies.State('id_filtre_distance_2', 'value'),
        dash.dependencies.State('id_filtre_matrice_2', 'value'),
        dash.dependencies.State('id_filtre_projet_2', 'value'),
        dash.dependencies.State('id_filtre_mesure_2', 'value'),
        dash.dependencies.State('id_normalisation_2', 'value'),
        dash.dependencies.State('id_metric_2', 'value'),
        dash.dependencies.State('id_varexp_2', 'value')]
    )
    def generate_profil_button_2(button, mode,
        filter_distance_1, filter_matrice_1, filter_project_1, filter_mesure_1, normalisation_1, metric_1, varexp_1,
        filter_distance_2, filter_matrice_2, filter_project_2, filter_mesure_2, normalisation_2, metric_2, varexp_2):

        fig1 = go.Figure()
        fig2 = go.Figure()
        result_dot_1 = html.P("")
        result_dot_2 = html.P("")
        if(button != None):
            if(normalisation_1 != None and metric_1 != None and varexp_1 != None and 
                normalisation_1 != '' and metric_1 != '' and varexp_1 != ''):
                ## Selection de la norme
                if(normalisation_1 == "norme_A"):
                    subs_target_1 = substances_A
                elif(normalisation_1 == "norme_C"):
                    subs_target_1 = substances_C

                df_data_1 = get_data(filter_distance_1, filter_matrice_1, filter_project_1, filter_mesure_1)
                if(len(df_data_1) > 0):
                    if(metric_1 == "mean"):
                        df_group_1 = df_data_1.groupby([conversion[varexp_1]]).mean()
                    elif(metric_1 == "median"):
                        df_group_1 = df_data_1.groupby([conversion[varexp_1]]).median()

                    df_dot_1 = dot_product_table(df_group_1[subs_target_1].dropna())
                    df_dot_1 = df_dot_1.reset_index()
                    df_dot_1[df_dot_1.columns[1:]] = round(df_dot_1[df_dot_1.columns[1:]] * 100, 2)

                    df_group_1 = df_group_1.reset_index()
                    df_group_1 = df_group_1[[conversion[varexp_1]] + subs_target_1].dropna()
                    df_group_1[subs_target_1] = round(df_group_1[subs_target_1] * 100, 2)
                    
                    df_count_1 = df_data_1.groupby([conversion[varexp_1]]).count()
                    df_count_1 = df_count_1.reset_index()
                    df_count_1 = df_count_1[[conversion[varexp_1]] + subs_target_1].dropna()

                    fig1.add_trace(
                        go.Bar(x=df_count_1[conversion[varexp_1]], y=df_count_1[df_count_1.columns[1]].values)
                    )
                    fig1.update_layout(
                        xaxis_showticklabels=True,
                        xaxis = dict(type='category'),
                        xaxis_title=conversion[varexp_1],
                        yaxis_title="Nombre d'échantillons"
                    )

                    result_1 = html.Div([
                        dash_table.DataTable(
                            id='table_1',
                            columns=[{"name" : conversion[varexp_1].replace("_", " "), "id" : conversion[varexp_1]}] + [{"name" : col.replace("-", " ").replace("_A", "").replace("_C", "") , "id" : col} for col in subs_target_1],
                            data= df_group_1.to_dict('records'),
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'height': 'auto',
                                'minWidth': '50px', 'width': '20px', 'maxWidth': '100px',
                                'whiteSpace': 'normal'
                            },
                            style_data_conditional=[
                                {
                                    'if': {
                                        'filter_query': '{' + col + '} >= ' + str(list_value[i]) + ' && {' + col + '} < ' + str(list_value[i + 1]),
                                        'column_id': col
                                    },
                                    'backgroundColor': color[0],
                                    'color': color[1]
                                }
                                for col in subs_target_1 for (i, color) in enumerate(zip(list_color, list_color_police))
                            ]
                        ),
                    ])

                    result_dot_1 = html.Div([
                        dash_table.DataTable(
                            id='table_dot_1',
                            columns=[{"name" : " ", "id" : "Variable_1"}] + [{"name" : col, "id" : col} for col in df_dot_1["Variable_1"].values],
                            data= df_dot_1.to_dict('records'),
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'height': 'auto',
                                'minWidth': '20px', 'width': '20px', 'maxWidth': '50px',
                                'whiteSpace': 'normal'
                            },
                        )
                    ])
                else:
                    result_1 = html.P("Pas de données disponibles")
            else:
                result_1 = html.P("Complétez les paramètres")

            if(normalisation_2 != None and metric_2 != None and varexp_2 != None and 
                normalisation_2 != '' and metric_2 != '' and varexp_2 != ''):
                ## Selection de la norme
                if(normalisation_2 == "norme_A"):
                    subs_target_2 = substances_A
                elif(normalisation_2 == "norme_C"):
                    subs_target_2 = substances_C

                df_data_2 = get_data(filter_distance_2, filter_matrice_2, filter_project_2, filter_mesure_2)
                if(len(df_data_2) > 0):
                    if(metric_2 == "mean"):
                        df_group_2 = df_data_2.groupby([conversion[varexp_2]]).mean()
                    elif(metric_2 == "median"):
                        df_group_2 = df_data_2.groupby([conversion[varexp_2]]).median()

                    df_dot_2 = dot_product_table(df_group_2[subs_target_2].dropna())
                    df_dot_2 = df_dot_2.reset_index()
                    df_dot_2[df_dot_2.columns[1:]] = round(df_dot_2[df_dot_2.columns[1:]] * 100, 2)

                    df_group_2 = df_group_2.reset_index()
                    df_group_2 = df_group_2[[conversion[varexp_2]] + subs_target_2].dropna()
                    df_group_2[subs_target_2] = round(df_group_2[subs_target_2] * 100, 2)

                    df_count_2 = df_data_2.groupby([conversion[varexp_2]]).count()
                    df_count_2 = df_count_2.reset_index()
                    df_count_2 = df_count_2[[conversion[varexp_2]] + subs_target_2].dropna()

                    fig2.add_trace(
                        go.Bar(x=df_count_1[conversion[varexp_1]], y=df_count_2[df_count_2.columns[1]].values)
                    )
                    fig2.update_layout(
                        xaxis_showticklabels=True,
                        xaxis = dict(type='category'),
                        xaxis_title=conversion[varexp_2],
                        yaxis_title="Nombre d'échantillons"
                    )

                    result_2 = html.Div([
                        dash_table.DataTable(
                            id='table_2',
                            columns=[{"name" : conversion[varexp_2].replace("_", " "), "id" : conversion[varexp_2]}] + [{"name" : col.replace("-", " ").replace("_A", "").replace("_C", "") , "id" : col} for col in subs_target_2],
                            data= df_group_2.to_dict('records'),
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'height': 'auto',
                                'minWidth': '50px', 'width': '20px', 'maxWidth': '100px',
                                'whiteSpace': 'normal'
                            },
                            style_data_conditional=[
                                {
                                    'if': {
                                        'filter_query': '{' + col + '} >= ' + str(list_value[i]) + ' && {' + col + '} < ' + str(list_value[i + 1]),
                                        'column_id': col
                                    },
                                    'backgroundColor': color[0],
                                    'color': color[1]
                                }
                                for col in subs_target_2 for (i, color) in enumerate(zip(list_color, list_color_police))
                            ]
                        ),
                    ])

                    result_dot_2 = html.Div([
                        dash_table.DataTable(
                            id='table_dot_2',
                            columns=[{"name" : " ", "id" : "Variable_1"}] + [{"name" : col, "id" : col} for col in df_dot_2["Variable_1"].values],
                            data= df_dot_2.to_dict('records'),
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'height': 'auto',
                                'minWidth': '20px', 'width': '20px', 'maxWidth': '50px',
                                'whiteSpace': 'normal'
                            },
                        )
                    ])
                else:
                    result_2 = html.P("Pas de données disponibles")
            else:
                result_2 = html.P("Complétez les paramètres")

            return (dbc.Row([
                dbc.Col(
                    [html.H5("Profil 1"),
                    result_1],
                    width=6
                ),
                dbc.Col(
                    [html.H5("Profil 2"),
                    result_2],
                    width=6
                )]),
                fig1,
                fig2,
                result_dot_1,
                result_dot_2
            )

    ## Gestion du bouton générer pour le mode 1 profil
    @app.callback(
        [dash.dependencies.Output('comparison_layout_1', 'children'),
        dash.dependencies.Output('chart_volume_main', 'figure'),
        dash.dependencies.Output('dot_cross_table', 'children')],
        [dash.dependencies.Input('generate_1', 'n_clicks')],
        [dash.dependencies.State('radio_mode', 'value'),
        dash.dependencies.State('id_filtre_distance_main', 'value'),
        dash.dependencies.State('id_filtre_matrice_main', 'value'),
        dash.dependencies.State('id_filtre_projet_main', 'value'),
        dash.dependencies.State('id_filtre_mesure_main', 'value'),
        dash.dependencies.State('id_normalisation_main', 'value'),
        dash.dependencies.State('id_metric_main', 'value'),
        dash.dependencies.State('id_varexp_main', 'value')]
    )
    def generate_profil_button_1(button, mode,
        filter_distance_1, filter_matrice_1, filter_project_1, filter_mesure_1, normalisation_1, metric_1, varexp_1):

        result_dot_1 = html.P("")
        fig = go.Figure()
        if(button != None):
            if(normalisation_1 != None and metric_1 != None and varexp_1 != None and 
                normalisation_1 != '' and metric_1 != '' and varexp_1 != ''):
                ## Selection de la norme
                if(normalisation_1 == "norme_A"):
                    subs_target = substances_A
                elif(normalisation_1 == "norme_C"):
                    subs_target = substances_C

                df_data_1 = get_data(filter_distance_1, filter_matrice_1, filter_project_1, filter_mesure_1)
                if(len(df_data_1[subs_target].dropna()) > 0):
                    if(metric_1 == "mean"):
                        df_group_1 = df_data_1.groupby([conversion[varexp_1]]).mean()
                    elif(metric_1 == "median"):
                        df_group_1 = df_data_1.groupby([conversion[varexp_1]]).median()

                    df_dot_1 = dot_product_table(df_group_1[subs_target].dropna())
                    df_dot_1 = df_dot_1.reset_index()
                    df_dot_1[df_dot_1.columns[1:]] = round(df_dot_1[df_dot_1.columns[1:]] * 100, 2)
                    
                    df_group_1 = df_group_1.reset_index()
                    df_group_1 = df_group_1[[conversion[varexp_1]] + subs_target].dropna()
                    df_group_1[subs_target] = round(df_group_1[subs_target] * 100, 2)

                    df_count_1 = df_data_1.groupby([conversion[varexp_1]]).count()
                    df_count_1 = df_count_1.reset_index()
                    df_count_1 = df_count_1[[conversion[varexp_1]] + subs_target].dropna()
                    

                    fig.add_trace(
                        go.Bar(x=df_count_1[conversion[varexp_1]], y=df_count_1[df_count_1.columns[1]].values),
                        
                    )
                    fig.update_layout(
                        xaxis_showticklabels=True,
                        xaxis_title=conversion[varexp_1],
                        xaxis = dict(type='category'),
                        yaxis_title="Nombre d'échantillons"
                    )

                    result_1 = html.Div([
                        dash_table.DataTable(
                            id='table_1',
                            columns=[{"name" : conversion[varexp_1].replace("_", " "), "id" : conversion[varexp_1]}] + [{"name" : col.replace("-", " ").replace("_A", "").replace("_C", "") , "id" : col} for col in subs_target],
                            data= df_group_1.to_dict('records'),
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'height': 'auto',
                                'minWidth': '50px', 'width': '20px', 'maxWidth': '100px',
                                'whiteSpace': 'normal'
                            },
                            style_data_conditional=[
                                {
                                    'if': {
                                        'filter_query': '{' + col + '} >= ' + str(list_value[i]) + ' && {' + col + '} < ' + str(list_value[i + 1]),
                                        'column_id': col
                                    },
                                    'backgroundColor': color[0],
                                    'color': color[1]
                                }
                                for col in subs_target for (i, color) in enumerate(zip(list_color, list_color_police))
                            ]
                        ),
                    ])

                    result_dot_1 = html.Div([
                        dash_table.DataTable(
                            id='table_dot_1',
                            columns=[{"name" : " ", "id" : "Variable_1"}] + [{"name" : col, "id" : col} for col in df_dot_1["Variable_1"].values],
                            data= df_dot_1.to_dict('records'),
                            style_table={'overflowX': 'auto'},
                            style_cell={
                                'height': 'auto',
                                'minWidth': '20px', 'width': '20px', 'maxWidth': '50px',
                                'whiteSpace': 'normal'
                            },
                        )
                    ])
                else:
                    result_1 = html.P("Pas de données disponibles")
            else:
                result_1 = html.P("Complétez les paramètres")

            return (result_1, fig, result_dot_1)
