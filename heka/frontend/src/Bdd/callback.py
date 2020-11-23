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
                uplaod_file(mzml_name, content_string)
            children = html.Div([
                        html.H5(mzml_name),
                        html.H6('a été chargé !'),
                    ])
            return children


    @app.callback([Output('table-analysis', 'data'),
                  Output('table-analysis', 'columns'),
                  Output('table-analysis', 'row_selectable')],
                  [Input('intermediate-value-analysis', 'children')])
    def update_output(jsonified_cleaned_data):
        df = pd.read_json(jsonified_cleaned_data, orient='split')
        selectable='single'
        return(df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], selectable)


    @app.callback([Output('selected-row-ids-analysis', 'children'),
                   Output('table-analysis', 'selected_rows')],
                  [Input('buttons-analysis', "n_clicks")],
                  [State('table-analysis', "selected_rows")])
    def update_output(n, derived_virtual_selected_rows):
        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []

        children = html.Div([
                        html.P(str(derived_virtual_selected_rows)
                        ),
                    ])
        return(children,[])

    @app.callback(Output('intermediate-value-analysis', 'children'), 
                  [Input('non-displayed', 'children')])
    def clean_data(value):
        query=f"""SELECT * FROM public.analysis;"""
        df = get_df_full_query(query)
        return df.to_json(date_format='iso', orient='split')


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



    @app.callback([Output('selected-row-ids-echantillon-test', 'children'),
                  Output('table-echantillon', 'selected_rows')],
                  [Input('buttons-launch-analysis', "n_clicks"),
                  Input('intermediate-value-echantillon', 'children')],
                  [State('table-echantillon', "selected_rows"),
                  State('threshold-positif', 'value'),
                  State('threshold-negatif', 'value')])
    def update_output(n, jsonified_cleaned_data, derived_virtual_selected_rows, pos, neg):
        if derived_virtual_selected_rows is None or derived_virtual_selected_rows==[]:
            return(html.Div(), [])

        df = pd.read_json(jsonified_cleaned_data, orient='split')
        children = html.Div(
                        [html.P('Lancer analayse sur :')]+
                        [html.P(df.mzml_file[df.index==i].values[0]) for i in derived_virtual_selected_rows]+
                        [html.P('avec un threshold positif de')]+
                        [html.P(pos)]+
                        [html.P('avec un threshold negatif de')]+
                        [html.P(neg)]
                    )
        return(children, [])
