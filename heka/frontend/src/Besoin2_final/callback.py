import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
import dash_html_components as html
import dash_table
import custom_components as cc

import os
import base64
import io
import csv

import Besoin2_final.helpers as hp
import json
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def register_callbacks(app):
    ## Génération du profil pour les échantillons
    @app.callback(
        [Output('warning', 'children'),
        Output('table_db_profil', 'data'),
        Output('table_db_profil', 'columns')],
        [Input('analyse', 'n_clicks')],
        [State('table_db', "selected_rows"),
        State("id_metric", "value"),
        State("id_normalisation", "value")]
    )
    def generation_profils(value, selected_rows, metric, normalisation):
        if (selected_rows == [] or selected_rows is None):
            result = html.P("Veuillez selectionner les échantillons à comparer",  style={'color':'red'})
        elif(metric is None or normalisation is None):
            result = html.P("Veuillez choisir une métrique et une normalisation pour l'analyse",  style={'color':'red'})
        else:
            if(normalisation == "norme_A"):
                subs_target = hp.substances_A
            else:
                subs_target = hp.substances_C

            df_result = hp.df[hp.df["id"].isin(selected_rows)]
            df_result = df_result[["id"] + subs_target]

            list_inter = df_result.values.tolist()
            if(metric == "mean"):
                list_inter.append(["Moyenne"] + [round(i, 2) for i in np.mean(df_result[subs_target])])
                df_result = pd.DataFrame(columns=list(df_result.columns), data=list_inter)
            elif(metric == "median"):
                list_inter.append(["Médiane"] + [round(i, 2) for i in np.median(df_result[subs_target], axis = 0)])
                df_result = pd.DataFrame(columns=list(df_result.columns), data=list_inter)

            result = html.P("")
            return (result, df_result.to_dict('records'), [{'name': i, 'id': i} for i in df_result.columns])

        return (result, [], [{'name': 'Charging ...', 'id': 'Charging ...'}])   
    
    ## Gestion du filtre projet
    @app.callback(
        Output('id_filtre_projet', 'options'),
        [Input('id_filtre_distance', 'value'),
        Input('id_filtre_matrice', 'value'),
        Input('id_filtre_mesure', 'value'),
        Input('table_db', 'data')]
    )
    def filter_dynamic_projet(value_distance, value_matrice, value_mesure, data):
        df_categories_filter = hp.get_categories()

        if(value_distance != None and value_distance != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["distance"].isin(value_distance))]

        if(value_matrice != None and value_matrice != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["matrice"].isin(value_matrice))]

        if(value_mesure != None and value_mesure != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["mesure"].isin(value_mesure))]

        return [{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories_filter["projet"].sort_values())]

    ## Gestion du filtre distance
    @app.callback(
        Output('id_filtre_distance', 'options'),
        [Input('id_filtre_projet', 'value'),
        Input('id_filtre_matrice', 'value'),
        Input('id_filtre_mesure', 'value'),
        Input('table_db', 'data')]
    )
    def filter_dynamic_distance(value_projet, value_matrice, value_mesure, data):
        df_categories_filter = hp.get_categories()

        if(value_projet != None and value_projet != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["projet"].isin(value_projet))]

        if(value_matrice != None and value_matrice != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["matrice"].isin(value_matrice))]

        if(value_mesure != None and value_mesure != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["mesure"].isin(value_mesure))]

        return [{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories_filter["distance"].sort_values())]


    ## Gestion du filtre matrice
    @app.callback(
        Output('id_filtre_matrice', 'options'),
        [Input('id_filtre_distance', 'value'),
        Input('id_filtre_projet', 'value'),
        Input('id_filtre_mesure', 'value'),
        Input('table_db', 'data')]
    )
    def filter_dynamic_matrice(value_distance, value_projet, value_mesure, data):
        df_categories_filter = hp.get_categories()

        if(value_distance != None and value_distance != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["distance"].isin(value_distance))]

        if(value_projet != None and value_projet != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["projet"].isin(value_projet))]

        if(value_mesure != None and value_mesure != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["mesure"].isin(value_mesure))]

        return [{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories_filter["matrice"].sort_values())]

    
    ## Gestion du filtre mesure
    @app.callback(
        Output('id_filtre_mesure', 'options'),
        [Input('id_filtre_distance', 'value'),
        Input('id_filtre_matrice', 'value'),
        Input('id_filtre_projet', 'value'),
        Input('table_db', 'data')]
    )
    def filter_dynamic_mesure(value_distance, value_matrice, value_projet, data):
        df_categories_filter = hp.get_categories()

        if(value_distance != None and value_distance != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["distance"].isin(value_distance))]

        if(value_matrice != None and value_matrice != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["matrice"].isin(value_matrice))]

        if(value_projet != None and value_projet != []):
            df_categories_filter = df_categories_filter[(df_categories_filter["projet"].isin(value_projet))]

        return [{"label" : str(category), "value" : str(category)} for category in pd.unique(df_categories_filter["mesure"].sort_values())]
    
    ## Génération des résultats de comparaison
    @app.callback(
        [Output('table_db_compare', 'data'),
        Output('table_db_compare', 'columns'),
        Output('table_profils', 'data'),
        Output('table_profils', 'columns'),
        Output('table_profils', 'style_data_conditional')],
        [Input('analyse_2', 'n_clicks')],
        [State('id_filtre_distance', 'value'),
        State('id_filtre_matrice', 'value'),
        State('id_filtre_projet', 'value'),
        State('id_filtre_mesure', 'value'),
        State('table_db', "selected_rows"),
        State("id_metric", "value"),
        State("id_normalisation", "value")]
    )
    def generable_table_profils(n_clicks, value_distance, value_matrice, value_projet, value_mesure, selected_rows, metric, normalisation):
        if (selected_rows is None or selected_rows == []):
            return ([], [{'name': 'Charging ...', 'id': 'Charging ...'}], [], [{'name': 'Charging ...', 'id': 'Charging ...'}], [])
        elif (metric == "" or metric is None or normalisation == "" or normalisation is None):
            return ([], [{'name': 'Charging ...', 'id': 'Charging ...'}], [], [{'name': 'Charging ...', 'id': 'Charging ...'}], [])
        else:
            if(normalisation == "norme_A"):
                subs_target = hp.substances_A
            else:
                subs_target = hp.substances_C

            df_result = hp.df[hp.df["id"].isin(selected_rows)]
            df_result = df_result[["id"] + subs_target]

            if(len(df_result.dropna()) == 0):
                return ([], [{'name': 'Charging ...', 'id': 'Charging ...'}], [], [{'name': 'Charging ...', 'id': 'Charging ...'}], [])
            else:
                if(metric == "mean"):
                    df_result = [round(i, 2) for i in np.mean(df_result[subs_target])]
                elif(metric == "median"):
                    df_result = [round(i, 2) for i in np.median(df_result[subs_target], axis=0)]

                df_compare = hp.df[-(hp.df["id"].isin(selected_rows))][hp.columns_ind + subs_target]

                if(value_distance != None and value_distance != []):
                    df_compare = df_compare[df_compare["Distance_à_la_source_km"].isin(value_distance)]

                if(value_matrice != None and value_matrice != []):
                    df_compare = df_compare[df_compare["Matrice"].isin(value_matrice)]

                if(value_projet != None and value_projet != []):
                    df_compare = df_compare[df_compare["Nom_du_projet"].isin(value_projet)]

                if(value_mesure != None and value_mesure != []):
                    df_compare = df_compare[df_compare["Type_de_point_de_mesure"].isin(value_mesure)]

                df_compare = df_compare.dropna(subset=subs_target)

                list_result = []
                for i in range(len(df_compare)):
                    cosine_result = cosine_similarity([df_result], [df_compare.iloc[i][subs_target]])[0][0]
                    if (cosine_result >= 0 and cosine_result <= 1):
                        list_result.append(cosine_result)
                    else:
                        list_result.append(0)
                
                df_compare["score"] = list_result
                df_compare = df_compare.sort_values(by=["score"], ascending=False)
                df_compare = df_compare.iloc[0:10]
                
                return (df_compare[["score"] + hp.columns_ind].to_dict('records'), [{'name': i, 'id': i} for i in df_compare[["score"] + hp.columns_ind].columns],
                    df_compare[[ "id", "score"] + subs_target].to_dict('records'), [{'name': i, 'id': i} for i in df_compare[[ "id", "score"] + subs_target].columns],
                    [
                    {
                        'if': {
                            'filter_query': '{' + col + '} >= ' + str(hp.list_value[i]) + ' && {' + col + '} < ' + str(hp.list_value[i + 1]),
                            'column_id': col
                        },
                        'backgroundColor': color[0],
                        'color': color[1]
                    }
                    for col in subs_target for (i, color) in enumerate(zip(hp.list_color, hp.list_color_police))
                ])

    ## Gestion du filtre projet
    @app.callback(
        [dash.dependencies.Output('id_filtre_projet_1_bis', 'options'),
        dash.dependencies.Output('id_filtre_projet_2_bis', 'options')],
        [dash.dependencies.Input('id_filtre_distance_1_bis', 'value'),
        dash.dependencies.Input('id_filtre_matrice_1_bis', 'value'),
        dash.dependencies.Input('id_filtre_mesure_1_bis', 'value'),
        dash.dependencies.Input('id_filtre_distance_2_bis', 'value'),
        dash.dependencies.Input('id_filtre_matrice_2_bis', 'value'),
        dash.dependencies.Input('id_filtre_mesure_2_bis', 'value'),
        dash.dependencies.Input('table_db', 'data')]
    )
    def filter_dynamic_projet_compare(value_distance_1, value_matrice_1, value_mesure_1, value_distance_2, value_matrice_2, value_mesure_2, data):
        df_categories_filter_1 = hp.get_categories()
        df_categories_filter_2 = hp.get_categories()
        
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
        [dash.dependencies.Output('id_filtre_distance_1_bis', 'options'),
        dash.dependencies.Output('id_filtre_distance_2_bis', 'options')],
        [dash.dependencies.Input('id_filtre_projet_1_bis', 'value'),
        dash.dependencies.Input('id_filtre_matrice_1_bis', 'value'),
        dash.dependencies.Input('id_filtre_mesure_1_bis', 'value'),
        dash.dependencies.Input('id_filtre_projet_2_bis', 'value'),
        dash.dependencies.Input('id_filtre_matrice_2_bis', 'value'),
        dash.dependencies.Input('id_filtre_mesure_2_bis', 'value'),
        dash.dependencies.Input('table_db', 'data')]
    )
    def filter_dynamic_distance_compare(value_projet_1, value_matrice_1, value_mesure_1, value_projet_2, value_matrice_2, value_mesure_2, data):
        df_categories_filter_1 = hp.get_categories()
        df_categories_filter_2 = hp.get_categories()
        
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
        [dash.dependencies.Output('id_filtre_matrice_1_bis', 'options'),
        dash.dependencies.Output('id_filtre_matrice_2_bis', 'options')],
        [dash.dependencies.Input('id_filtre_distance_1_bis', 'value'),
        dash.dependencies.Input('id_filtre_projet_1_bis', 'value'),
        dash.dependencies.Input('id_filtre_mesure_1_bis', 'value'),
        dash.dependencies.Input('id_filtre_distance_2_bis', 'value'),
        dash.dependencies.Input('id_filtre_projet_2_bis', 'value'),
        dash.dependencies.Input('id_filtre_mesure_2_bis', 'value'),
        dash.dependencies.Input('table_db', 'data')]
    )
    def filter_dynamic_matrice_compare(value_distance_1, value_projet_1, value_mesure_1, value_distance_2, value_projet_2, value_mesure_2, data):
        df_categories_filter_1 = hp.get_categories()
        df_categories_filter_2 = hp.get_categories()
        
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
        [dash.dependencies.Output('id_filtre_mesure_1_bis', 'options'),
        dash.dependencies.Output('id_filtre_mesure_2_bis', 'options')],
        [dash.dependencies.Input('id_filtre_distance_1_bis', 'value'),
        dash.dependencies.Input('id_filtre_matrice_1_bis', 'value'),
        dash.dependencies.Input('id_filtre_projet_1_bis', 'value'),
        dash.dependencies.Input('id_filtre_distance_2_bis', 'value'),
        dash.dependencies.Input('id_filtre_matrice_2_bis', 'value'),
        dash.dependencies.Input('id_filtre_projet_2_bis', 'value'),
        dash.dependencies.Input('table_db', 'data')]
    )
    def filter_dynamic_mesure_compare(value_distance_1, value_matrice_1, value_projet_1, value_distance_2, value_matrice_2, value_projet_2, data):
        df_categories_filter_1 = hp.get_categories()
        df_categories_filter_2 = hp.get_categories()
        
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


    @app.callback(
        Output("collapse", "is_open"),
        [Input("collapse-button", "n_clicks")],
        [State("collapse", "is_open")]
    )
    def toggle_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        [Output("warning_type_file", "children"),
        Output("table_db", "data"),
        Output("table_db", "columns")],
        [Input("upload_data_echantillon", "filename"),
        Input("upload_data_echantillon", "contents")]
    )
    def load_csv(name, data_string):
        if(name.find(".csv") == -1):
            return (html.P("Attention le fichier importé n'est pas au bon format (format à utiliser '.csv').", style={'color':'red'}), [], [{'name': 'Charging ...', 'id': 'Charging ...'}])
        else:
            content_type, content_string = data_string.split(',')
            decoded = base64.b64decode(content_string)
            data = decoded.decode('utf-8')
            data = data.splitlines()
            data = [row.split(";") for row in data]

            hp.df = pd.DataFrame(data=data[1:], columns=data[0])
            hp.df = hp.df.replace('', np.nan)
            for col in (hp.substances + hp.total_homologue + ['Total_DIOXINE', 'Total_FURANE']):
                hp.df[col] = hp.df[col].astype(str)
                hp.df[col] = [float(str(a.replace(',', '.'))) for a in hp.df[col].values]
            
            ## Normalisation A
            hp.df["total sub 2378"] = 0
            for sub in hp.substances:
                hp.df["total sub 2378"] += hp.df[sub]
            for sub in hp.substances:
                hp.df[sub + '_A'] = hp.df[sub]  / hp.df["total sub 2378"]

            ## Normalisation C
            table_norme_C = hp.df.copy()

            for col in hp.total_homologue:
                hp.df["total homologue"] = 0
                hp.df["total homologue"] += hp.df[col]
            table_norme_C = hp.df[hp.df["total homologue"] > 0]

            substance_in = {}
            for homologue in hp.total_homologue:
                if(homologue != "OCDD" and homologue != "OCDF"):
                    list_sub = []
                    text_ref_homologue = homologue.replace("Total_", "")
                    table_norme_C[text_ref_homologue] = 0
                    for sub in hp.substances:
                        if sub.find(text_ref_homologue) != -1:
                            list_sub.append(sub)
                            table_norme_C[text_ref_homologue] += table_norme_C[sub]
                    substance_in[homologue] = list_sub
                    text_ref_homologue_2 = text_ref_homologue + "_2"
                    table_norme_C[text_ref_homologue_2] = table_norme_C[text_ref_homologue] * 0.9
                    table_norme_C = table_norme_C[table_norme_C[text_ref_homologue_2] <= table_norme_C[homologue]]
                else:
                    substance_in[homologue] = [homologue]

            table_norme_C['TOTAL PCDD'] = table_norme_C['TCDD'] + table_norme_C['PeCDD'] + table_norme_C['HxCDD'] + table_norme_C['HpCDD'] + table_norme_C['OCDD']
            table_norme_C['TOTAL PCDF'] = table_norme_C['TCDF'] + table_norme_C['PeCDF'] + table_norme_C['HxCDF'] + table_norme_C['HpCDF'] + table_norme_C['OCDF'] 

            for homologue in hp.total_homologue:
                for sub in substance_in[homologue]:
                    if sub == 'OCDD':
                        table_norme_C['OCDD'] = table_norme_C['OCDD'] / table_norme_C['TOTAL PCDD']
                    elif sub == 'OCDF':
                        table_norme_C['OCDF'] = table_norme_C['OCDF'] / table_norme_C['TOTAL PCDF']
                    else:
                        table_norme_C[sub] = table_norme_C[sub] / table_norme_C[homologue]
            table_norme_C = table_norme_C.fillna(0)
            table_norme_C = table_norme_C.replace(np.inf, 0)
            renaming = { pre : nex for (pre, nex) in zip(hp.substances, hp.substances_C) }
            table_norme_C = table_norme_C.rename(columns = renaming)

            hp.df = hp.df.merge(table_norme_C[hp.substances_C], how='left', left_index=True, right_index=True)

            hp.set_all_data(hp.df, "data_ineris")

            hp.df[hp.substances_A] = round(hp.df[hp.substances_A] * 100, 2)
            hp.df[hp.substances_C] = round(hp.df[hp.substances_C] * 100, 2)
            hp.df["id"] = hp.df.index

            hp.df = hp.df[- hp.df['OCDD_A'].isnull()]

            hp.df_categories_final = hp.df[[hp.conversion[key] for key in hp.conversion]].groupby([hp.conversion[key] for key in hp.conversion]).count().reset_index()
            hp.df_categories_final.rename(columns={hp.conversion[key] : key for key in hp.conversion})

            return (html.P(""), hp.df[hp.columns_ind + hp.substances].to_dict('records'), [{'name': i, 'id': i} for i in hp.df[hp.columns_ind + hp.substances].columns])


    @app.callback(
        Output("loading-0", "children"),
        [Input("upload_data_echantillon", "n_intervals")]
    )
    def refresh_table(nb_inter):
        table = dash_table.DataTable(
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
        return table

    @app.callback(
        Output("chart_resultat", "figure"),
        [Input("analyse_3", "n_clicks")],
        [State("id_filtre_projet_1_bis", "value"),
        State("id_filtre_projet_2_bis", "value"),
        State("id_filtre_matrice_1_bis", "value"),
        State("id_filtre_matrice_2_bis", "value"),
        State("id_filtre_distance_1_bis", "value"),
        State("id_filtre_distance_2_bis", "value"),
        State("id_filtre_mesure_1_bis", "value"),
        State("id_filtre_mesure_2_bis", "value"),
        State("id_metric", "value"),
        State("id_normalisation", "value"),
        State('table_db', "selected_rows")]
    )
    def trace_impact(n_clicks, projet_1, projet_2, matrice_1, matrice_2, distance_1, distance_2, mesure_1, mesure_2, metric, normalisation, selected_rows):
        fig = go.Figure()
        if (selected_rows is None or selected_rows == []):
            return fig
        elif(metric is None and normalisation is None):
            return fig
        else:
            if(normalisation == "norme_A"):
                subs_target = hp.substances_A
            else:
                subs_target = hp.substances_C

            df_result = hp.df[hp.df["id"].isin(selected_rows)]
            df_result = df_result[["id"] + subs_target]

            if(len(df_result.dropna()) == 0):
                return fig
            else:
                if(metric == "mean"):
                    df_result = [round(i, 2) for i in np.mean(df_result[subs_target])]
                elif(metric == "median"):
                    df_result = [round(i, 2) for i in np.median(df_result[subs_target], axis=0)]
                
                ## Generer le referent
                df_compare_1 = hp.df.copy()
                
                if(distance_1 != None and distance_1 != []):
                    df_compare_1 = df_compare_1[df_compare_1["Distance_à_la_source_km"].isin(distance_1)]

                if(matrice_1 != None and matrice_1 != []):
                    df_compare_1 = df_compare_1[df_compare_1["Matrice"].isin(matrice_1)]

                if(projet_1 != None and projet_1 != []):
                    df_compare_1 = df_compare_1[df_compare_1["Nom_du_projet"].isin(projet_1)]

                if(mesure_1 != None and mesure_1 != []):
                    df_compare_1 = df_compare_1[df_compare_1["Type_de_point_de_mesure"].isin(mesure_1)]

                if(metric == "mean"):
                    referent = [round(i, 2) for i in np.mean(df_compare_1[subs_target])]
                elif(metric == "median"):
                    referent = [round(i, 2) for i in np.median(df_compare_1[subs_target], axis = 0)]

                ## Selectionner les comparants
                df_compare_2 = hp.df.copy()
                
                if(distance_2 != None and distance_2 != []):
                    df_compare_2 = df_compare_2[df_compare_2["Distance_à_la_source_km"].isin(distance_2)]

                if(matrice_2 != None and matrice_2 != []):
                    df_compare_2 = df_compare_2[df_compare_2["Matrice"].isin(matrice_2)]

                if(projet_2 != None and projet_2 != []):
                    df_compare_2 = df_compare_2[df_compare_2["Nom_du_projet"].isin(projet_2)]

                if(mesure_2 != None and mesure_2 != []):
                    df_compare_2 = df_compare_2[df_compare_2["Type_de_point_de_mesure"].isin(mesure_2)]
                
                ## Calcul du consine similarité
                list_result = []
                for i in range(len(df_compare_2)):
                    cosine_result = cosine_similarity([referent], [df_compare_2.iloc[i][subs_target]])[0][0]
                    if (cosine_result >= 0 and cosine_result <= 1):
                        list_result.append(cosine_result)
                    else:
                        list_result.append(0)

                result_sample = cosine_result = cosine_similarity([referent], [df_result])[0][0]

                ## Trace l'histogramme
                fig.add_trace(
                    go.Histogram(
                        x=list_result,
                        nbinsx=200,
                        name="Comparants"
                    )
                )

                fig.add_trace(
                    go.Scatter(
                        x=[result_sample, result_sample],
                        y=[0, len(list_result) / 5],
                        mode="lines",
                        name="Echantillons selectionnés",
                        line=dict(color="rgb(205, 3, 3)"),
                        showlegend=True
                    )
                )

                fig.update_layout(
                    xaxis_showticklabels=True,
                    xaxis_title="Cosine Similariy",
                    yaxis_title="Nombre d'échantillons"
                )

                return fig