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
from Bdd_analysis.helpers import *


# Folder that contains all mzml files and that after each deployment get synchronized with GS bucket
FILE_PATH_BASE = '/heka/storage/'



# Function to call all callbacks 
def register_callbacks(app):


    @app.callback([Output('table-analysis', 'data'),
                  Output('table-analysis', 'columns')],
                  [Input('intermediate-value-analysis', 'children')])
    def update_output(jsonified_cleaned_data):
        df = pd.read_json(jsonified_cleaned_data, orient='split')
        # selectable='single'
        return(df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns])


    @app.callback([Output('selected-row-ids-analysis', 'children'),
                   Output('table-analyse-macro', 'selected_rows')],
                  [Input('buttons-analysis', "n_clicks")],
                  [State('table-analyse-macro', "selected_rows")])
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
        # query=f"""SELECT * FROM public.analysis;"""
        query="""SELECT analysis_files.id_analysis, mzml_files.id_mzml, mzml_files.mzml_file,
                ionisation, acquisition_mode, date_analysis, threshold_positif, threshold_negatif, bdd
                FROM analysis_files LEFT JOIN mzml_files 
                ON analysis_files.id_mzml=mzml_files.id_mzml ORDER BY 1, 2"""
        df = get_df_full_query(query)
        return df.to_json(date_format='iso', orient='split')


    @app.callback([Output('table-analyse-macro', 'data'),
                  Output('table-analyse-macro', 'columns'),
                  Output('table-analyse-macro', 'row_selectable')],
                  [Input('intermediate-value-analyse-macro', 'children')])
    def update_output(jsonified_cleaned_data):
        df = pd.read_json(jsonified_cleaned_data, orient='split')
        selectable='multi'
        return(df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], selectable)


    @app.callback(Output('selected-row-ids-analyse-macro', 'children'),
                  [Input('table-analyse-macro', "selected_rows"),
                  Input('intermediate-value-analyse-macro', 'children')])
    def update_output(derived_virtual_selected_rows, jsonified_cleaned_data):
        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []

        df = pd.read_json(jsonified_cleaned_data, orient='split')
        children = html.Div([
                        html.P(', '.join([df.mzml_file[df.index==i].values[0] for i in derived_virtual_selected_rows])
                        ),
                    ])
        return(children)

    @app.callback(Output('intermediate-value-analyse-macro', 'children'), 
                  [Input('non-displayed', 'children')])
    def clean_data(value):
        query=f"""SELECT * FROM public.analysis;"""
        df = get_df_full_query(query)
        return df.to_json(date_format='iso', orient='split')

