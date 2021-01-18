#imports for dash callbacks
import dash
from dash.dependencies import Input, Output, State
import dash_html_components as html
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
from datetime import datetime, timedelta
# some helper functions
from Besoin3ech.helpers import *




# Function to call all callbacks 
def register_callbacks(app):

    @app.callback([Output('treated-samples', 'data'),
                  Output('treated-samples', 'columns'),
                  Output('treated-samples', 'row_selectable')],
                  [Input('intermediate-value-sample', 'children')])
    def update_output(jsonified_cleaned_data):
        selectable='multi'
        if jsonified_cleaned_data==None:
            return([], [{'name': 'Charging ...', 'id': 'Charging ...'}], selectable)
        df = pd.read_json(jsonified_cleaned_data, orient='split')
        return(df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], selectable)



    @app.callback(Output('intermediate-value-sample', 'children'), 
                  [Input('launch-analysis-ech', 'n_clicks'),
                  Input('hidden-button', 'n_clicks'),
                  Input('hidden-button-1', 'n_clicks')],
                  [State('my-date-picker-range-ech', 'start_date'),
                  State('my-date-picker-range-ech', 'end_date')])
    def clean_data(n, n1, n2, start, end):
        query=f"""SELECT regressor_results.date, regressor_results.model FROM 
        regressor_results LEFT JOIN blacklist_besoin3 
        ON regressor_results.date=blacklist_besoin3.date
        AND regressor_results.model=blacklist_besoin3.model
        WHERE blacklist_besoin3.model IS NULL AND blacklist_besoin3.date IS NULL
        AND '{start}' <= regressor_results.date AND regressor_results.date <= '{end}'
        GROUP BY 1,2
        ORDER BY 1 DESC
        LIMIT 300"""
        df = get_df_full_query(query)
        return df.to_json(date_format='iso', orient='split')


    @app.callback(
        [Output('my-date-picker-range-ech', 'start_date'),
        Output('my-date-picker-range-ech', 'end_date'),
        Output('launch-analysis-ech', 'n_clicks')],
        [Input('test', 'children')])
    def update_output(n):
        query=f"""SELECT max(date) FROM public.regressor_results;"""
        df = get_df_full_query(query)
        end = datetime.utcfromtimestamp(df.values[0][0].tolist()/1e9)
        start = (end-timedelta(days=7))
        return(start,end,1)


    @app.callback(Output('launched-analysis', 'figure'), 
                  [Input('launch-analysis-ech', 'n_clicks')],
                  [State('my-date-picker-range-ech', 'start_date'),
                  State('my-date-picker-range-ech', 'end_date')])
    def clean_data(n, start, end):
        if start==None or end==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300
            )
            return(fig)
        fig = tasks(start, end)
        return(fig)


    @app.callback([Output('output-data-blacklist', 'children'),
                   Output('treated-samples', 'selected_rows'),
                   Output('hidden-button-1', 'n_clicks')],
                  [Input('blacklist-sample', "n_clicks")],
                  [State('intermediate-value-sample', 'children'),
                  State('treated-samples', "selected_rows"),
                  State('hidden-button-1', 'n_clicks')])
    def update_output(n, jsonified_cleaned_data, derived_virtual_selected_rows, n1):
        n1 = 0 if n1==None else n1
        if jsonified_cleaned_data==None:
            return(html.Div(), derived_virtual_selected_rows, n1+1)
        if derived_virtual_selected_rows is None or derived_virtual_selected_rows==[]:
            return(html.Div(), [], n1+1)

        df = pd.read_json(jsonified_cleaned_data, orient='split')
        df['date_beaut'] = df.date.dt.strftime('%Y-%m-%d %H:%M:%S')
        dates=[df[['date_beaut', 'model']][df.index==i].values[0] for i in derived_virtual_selected_rows]
        for i in dates:
            try:
                add_2_blacklist_besoin3(i)
            except:
                return(html.Div(html.P('Erreur : échantillion déjà en base')), [], n1+1)

        children = html.Div(
                        [html.P('Blacklister :')]+
                        [html.P(str(df[['date_beaut', 'model']][df.index==i].values[0])) for i in derived_virtual_selected_rows]
                    )
        return(children, [], n1+1)


    @app.callback(Output('intermediate-value-sample-blacklisted', 'children'), 
                  [Input('launch-analysis-ech', 'n_clicks'),
                  Input('hidden-button', 'n_clicks'),
                  Input('hidden-button-1', 'n_clicks')],
                  [State('my-date-picker-range-ech', 'start_date'),
                  State('my-date-picker-range-ech', 'end_date')])
    def clean_data(n, n1, n2, start, end):
        query=f"""SELECT * FROM blacklist_besoin3"""
        # WHERE '{start}' <= date and date <= '{end}'
        # GROUP BY 1,2 ORDER BY 1 DESC, 2 LIMIT 300;"""
        df = get_df_full_query(query)
        return df.to_json(date_format='iso', orient='split')

    @app.callback([Output('black-listed-samples', 'data'),
                  Output('black-listed-samples', 'columns'),
                  Output('black-listed-samples', 'row_selectable')],
                  [Input('intermediate-value-sample-blacklisted', 'children')])
    def update_output(jsonified_cleaned_data):
        selectable='multi'
        if jsonified_cleaned_data==None:
            return([], [{'name': 'Charging ...', 'id': 'Charging ...'}], selectable)
        df = pd.read_json(jsonified_cleaned_data, orient='split')
        return(df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], selectable)


    @app.callback([Output('output-data-whitelist', 'children'),
                   Output('black-listed-samples', 'selected_rows'),
                   Output('hidden-button', 'n_clicks')],
                  [Input('white-list-sample', "n_clicks")],
                  [State('intermediate-value-sample-blacklisted', 'children'),
                  State('black-listed-samples', "selected_rows"),
                  State('hidden-button', 'n_clicks')])
    def update_output(n, jsonified_cleaned_data, derived_virtual_selected_rows, n1):
        n1 = 0 if n1==None else n1
        if jsonified_cleaned_data==None:
            return(html.Div(), derived_virtual_selected_rows, n1+1)
        if derived_virtual_selected_rows is None or derived_virtual_selected_rows==[]:
            return(html.Div(), [], n1+1)

        df = pd.read_json(jsonified_cleaned_data, orient='split')
        df['date_beaut'] = df.date.dt.strftime('%Y-%m-%d %H:%M:%S')
        dates=[df[['date_beaut', 'model']][df.index==i].values[0] for i in derived_virtual_selected_rows]
        for i in dates:
            try:
                query=f"DELETE FROM blacklist_besoin3 WHERE date='{i[0]}' AND model = '{i[1]}'"
                run_query(query)
            except:
                return(html.Div(html.P('Erreur')), [], n1+1)

        children = html.Div(
                        [html.P('Whitelister :')]+
                        [html.P(str(df[['date_beaut', 'model']][df.index==i].values[0])) for i in derived_virtual_selected_rows]
                    )
        return(children, [], n1+1)
