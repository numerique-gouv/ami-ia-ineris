#imports for dash callbacks
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import plotly.express as px
import dash_table as dt
# pymzml is a python ilbrary that handles mzml files
import pymzml
# brainpy is a library that helps calculating theoric isotopic profiles
from brainpy import isotopic_variants
# known useful libraries
import os
import re
import pandas as pd
import numpy as np
import time
# to ind peaks from chromato
from scipy.signal import find_peaks
# to calculate smilarity scores
from scipy import spatial
import datetime
# some helper functions
from Bdd.helpers import *


# Folder that contains all mzml files and that after each deployment get synchronized with GS bucket
FILE_PATH_BASE = '/heka/storage/'



# Function to call all callbacks 
def register_callbacks(app):
    @app.callback(Output('output-data-upload', 'children'),
                  [Input('upload-data-echantillon', 'contents')],
                  [State('upload-data-echantillon', 'filename'),
                   State('upload-data-echantillon', 'last_modified')])
    def update_output(list_of_contents, list_of_names, list_of_dates):
        if list_of_contents is not None:
            for mzml_content, mzml_name, d in zip(list_of_contents, list_of_names, list_of_dates):
                content_type, content_string = mzml_content.split(',')
                ionisation= 'POS' if 'pos' in mzml_name[-15:] else 'NEG'
                mzml_in_db = get_if_mzml_in_db(ionisation+'\\'+mzml_name)
                if mzml_in_db:
                    return(html.Div([html.H5(mzml_name), html.H6('est déjà en base')]))
                else:
                    uplaod_file(mzml_name, content_string)
            children = html.Div([
                        html.H5(mzml_name),
                        html.H6('a été chargé !'),
                    ])
            return children



    @app.callback([Output('table-echantillon', 'data'),
                  Output('table-echantillon', 'columns'),
                  Output('table-echantillon', 'row_selectable')],
                  [Input('intermediate-value-echantillon', 'children')])
    def update_output(jsonified_cleaned_data):
        df = pd.read_json(jsonified_cleaned_data, orient='split')
        selectable='multi'
        return(df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], selectable)


    @app.callback(Output('selected-row-ids-echantillon', 'children'),
                  [Input('table-echantillon', "selected_rows"),
                  Input('intermediate-value-echantillon', 'children')])
    def update_output(derived_virtual_selected_rows, jsonified_cleaned_data):
        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []

        df = pd.read_json(jsonified_cleaned_data, orient='split')
        children = html.Div([
                        html.P(', '.join([df.mzml_file[df.index==i].values[0] for i in derived_virtual_selected_rows])
                        ),
                    ])
        return(children)

    @app.callback(Output('intermediate-value-echantillon', 'children'), 
                  [Input('non-displayed', 'children')])
    def clean_data(value):
        query=f"""SELECT * FROM public.mzml_files;"""
        df = get_df_full_query(query)
        return df.to_json(date_format='iso', orient='split')



    @app.callback(Output('molecule-bdd', 'options'),
                  [Input('non-displayed', 'children')])
    def clean_data(value):
        query=f"""SELECT source FROM public.molecules GROUP BY 1;"""
        df = get_df_full_query(query)
        sources = df.T.values[0]
        return([{"label": i,"value": i} for i in sources])


    @app.callback([Output('confirm', 'displayed'),
                   Output('confirm', 'message')],
                  [Input('launch-analysis', "n_clicks")],
                  [State('intermediate-value-echantillon', 'children'),
                  State('table-echantillon', "selected_rows"),
                  State('threshold-positif', 'value'),
                  State('threshold-negatif', 'value'),
                  State('molecule-bdd', 'value')])
    def display_confirm(n, jsonified_cleaned_data, derived_virtual_selected_rows, pos, neg, value):
        if derived_virtual_selected_rows is None or derived_virtual_selected_rows==[] or value is None or value==[]:
            return(False, '')

        df = pd.read_json(jsonified_cleaned_data, orient='split')
        mzml_files=[df.mzml_file[df.index==i].values[0] for i in derived_virtual_selected_rows]
        # if len(mzml_files)!=0:
        #     launch_analysis(str(pos), str(neg), value, mzml_files)
        message = 'Lancer analayse sur : '+' '.join([df.mzml_file[df.index==i].values[0] for i in derived_virtual_selected_rows])+' avec un threshold positif de '+str(pos)+' avec un threshold negatif de '+str(neg)+' avec les BDDs '+str(value)
        return(True, message)



    @app.callback([Output('selected-row-ids-echantillon-test', 'children'),
                  Output('table-echantillon', 'selected_rows')],
                  [Input('confirm', 'submit_n_clicks')],
                  [State('intermediate-value-echantillon', 'children'),
                  State('table-echantillon', "selected_rows"),
                  State('threshold-positif', 'value'),
                  State('threshold-negatif', 'value'),
                  State('molecule-bdd', 'value')])
    def update_output(n, jsonified_cleaned_data, derived_virtual_selected_rows, pos, neg, value):
        if derived_virtual_selected_rows is None or derived_virtual_selected_rows==[] or value is None or value==[]:
            return(html.Div(), [])

        df = pd.read_json(jsonified_cleaned_data, orient='split')
        mzml_files=[df.mzml_file[df.index==i].values[0] for i in derived_virtual_selected_rows]
        if len(mzml_files)!=0:
            launch_analysis(str(pos), str(neg), value, mzml_files)
        children = html.Div(
                        [html.P('Analyse lancée sur :')]+
                        [html.P(df.mzml_file[df.index==i].values[0]) for i in derived_virtual_selected_rows]+
                        [html.P('avec un threshold positif de')]+
                        [html.P(pos)]+
                        [html.P('avec un threshold negatif de')]+
                        [html.P(neg)]+
                        [html.P('avec les BDDs')]+
                        [html.P(str(value))]
                    )
        return(children, [])
