#imports for dash callbacks
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import plotly.express as px
import dash_table as dt
from dash_table.Format import Format
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
from Boucle_retour.helpers import *


# Folder that contains all mzml files and that after each deployment get synchronized with GS bucket
FILE_PATH_BASE = '/heka/storage/'



# Function to call all callbacks 
def register_callbacks(app):
    @app.callback([Output('table-echantillon-resultat', 'data'),
                  Output('table-echantillon-resultat', 'columns'),
                  Output('table-echantillon-resultat', 'row_selectable'),
                  Output('triggerd', 'children'),
                  # Output('table-echantillon-resultat', 'tooltip_data'),
                  # Output('table-echantillon-resultat', 'fixed_columns')
                  ],
                  [Input('intermediate-value-echantillon-resultat', 'children'),
                  Input('apply-lvl', 'n_clicks')],
                  [State('lvl-dropdown', 'value')])
    def update_output(jsonified_cleaned_data, n, lvl):
        ctx = dash.callback_context
        if not ctx.triggered:
            button_id = 'No clicks yet'
        else:
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        df = pd.read_json(jsonified_cleaned_data, orient='split')
        df['Mode ionisation'] = df['mzml_file'].apply(lambda x : 'POS' if 'pos' in x[-15:] else 'NEG')
        df['mzml_file'] = df['mzml_file'].apply(lambda x : x[4:])
        if button_id == 'apply-lvl':
            lvl = '' if lvl is None else lvl
            df['validation'] = lvl
        df = df.round({'prob':2, 'rt_diff_abs':2, 'scholle_similarity_10':2,
                       'scholle_similarity_20':2, 'scholle_similarity_40':2,
                       'cosine_similarity_10':2, 'cosine_similarity_20':2, 'cosine_similarity_40':2,
                       'cosine_similarity_isotopic_mod':4, 'mass':4, 'prob_no_rt':2})
        df['retention_time_exp1'] = df['retention_time_exp'].round(2) 
        df = df.rename(columns={'mzml_file':'Fichier mzML', 'molecule_name': 'Nom molécule', 'prob': 'Score RT', 'cas': 'CAS',
                             'formula': 'Formule', 'mass': 'Masse', 'source': 'Source BDD', 'tic': 'Tic', 
                             'retention_time_exp1': 'RT exp', 'rt_diff_abs': 'RT diff', 'flag_peak_number_exp_20': 'Flag 20',
                             'flag_peak_number_exp_10': 'Flag 10', 'cosine_similarity_10': 'Cos 10',
                             'cosine_similarity_20': 'Cos 20', 'scholle_similarity_10': 'Scholle 10', 
                             'scholle_similarity_20': 'Scholle 20', 
                             'flag_peak_number_exp_40': 'Flag 40', 'cosine_similarity_40': 'Cos 40', 
                             'scholle_similarity_40': 'Scholle 40', 'cosine_similarity_isotopic_mod': 'Isotopic',
                             'prob_no_rt': 'Score no RT', 'acquisition_mode': 'Acq Mode', 'validation': 'validation'})
        add_columns = ['id_mzml', 'id_molecule', 'id_analysis', 'retention_time_exp']
        df = df[['Fichier mzML', 'Nom molécule', 'Mode ionisation', 'Acq Mode', 'Source BDD', 'Score RT', 'validation', 
                  'Tic', 'RT exp', 'RT diff', 'Flag 20', 'Cos 20', 'Scholle 20',  'Flag 40', 'Cos 40', 
                  'Scholle 40', 'Isotopic', 'Flag 10', 'Cos 10', 'Scholle 10', 'Score no RT', 'CAS', 
                  'Formule', 'Masse']+add_columns]

        # fixed_columns={'headers': True, 'data': 1}
        selectable='single'
        data=df.to_dict('records')
        # tooltip_data=[{
        #           col: f"{df[col][i]}"
        #           for col in df.columns} for i in range(0,df.shape[0])]
        return(df.to_dict('records'), [{'name': i, 'id': i, 'editable': (i=='validation')} for i in df.columns], selectable, button_id)


    @app.callback(Output('selected-row-ids-echantillon-resultat', 'children'),
                  [Input('table-echantillon-resultat', "selected_rows"),
                  Input('intermediate-value-echantillon-resultat', 'children')])
    def update_output(derived_virtual_selected_rows, jsonified_cleaned_data):
        if derived_virtual_selected_rows is None:
            derived_virtual_selected_rows = []

        df = pd.read_json(jsonified_cleaned_data, orient='split')
        children = html.Div([
                        html.P(', '.join([df.mzml_file[df.index==i].values[0] for i in derived_virtual_selected_rows])
                        ),
                    ])
        return(children)


    @app.callback(Output('intermediate-value-echantillon-resultat', 'children'), 
                  [Input('non-displayed-resultat', 'children'),
                  Input('my-range-slider', 'value'),
                  Input('analysis-dropdown', 'value'),
                  Input('file-dropdown', 'value'),
                  Input('booleanswitch-dash', 'on'),
                  Input('source-bdd', 'value')
                  ])
    def clean_data(chi, slider, analysis, file, toggle, source):
        if analysis == None:
            raise PreventUpdate
        if file == None:
            file="None"
        file="'"+file+"'"
        if file=="'None'":
            file='mzml_file'
        if source == None:
            source="None"
        source="'"+source+"'"
        if source=="'None'":
            source='source'
        if toggle==False:
            query=f"""SELECT mzml_file, molecule_name, round(prob, 2) AS prob, cas, formula, mass, source, round(tic) AS Tic, 
                      retention_time_exp , round(rt_diff_abs, 2) AS rt_diff_abs, 
                      flag_peak_number_exp_20, round(cosine_similarity_20, 3) AS cosine_similarity_20, 
                      round(scholle_similarity_20, 3) AS scholle_similarity_20, flag_peak_number_exp_40, 
                      round(cosine_similarity_40, 3) AS cosine_similarity_40, round(scholle_similarity_40, 3) AS scholle_similarity_40, 
                      round(cosine_similarity_isotopic_mod, 4) AS cosine_similarity_isotopic_mod,
                      prob_no_rt, id_mzml, id_molecule, id_analysis, flag_peak_number_exp_10, cosine_similarity_10,
                      scholle_similarity_10, validation, acquisition_mode
                      FROM scores 
                      WHERE id_analysis = {analysis}
                      AND mzml_file={file}
                      AND prob <= {slider[1]} AND prob >= {slider[0]}
                      AND source = {source}
                      AND retention_time_exp < 20
                      ORDER BY 3 DESC;"""
        elif toggle==True:
            query=f"""SELECT mzml_file, molecule_name, round(prob, 2) AS prob, cas, formula, mass, source, round(tic) AS Tic, 
                      retention_time_exp , round(rt_diff_abs, 2) AS rt_diff_abs, 
                      flag_peak_number_exp_20, round(cosine_similarity_20, 3) AS cosine_similarity_20, 
                      round(scholle_similarity_20, 3) AS scholle_similarity_20, flag_peak_number_exp_40, 
                      round(cosine_similarity_40, 3) AS cosine_similarity_40, round(scholle_similarity_40, 3) AS scholle_similarity_40, 
                      round(cosine_similarity_isotopic_mod, 4) AS cosine_similarity_isotopic_mod,
                      prob_no_rt, id_mzml, id_molecule, id_analysis, flag_peak_number_exp_10, cosine_similarity_10,
                      scholle_similarity_10, validation, acquisition_mode
                      FROM scores 
                      WHERE id_analysis = {analysis}
                      AND mzml_file={file}
                      AND prob <= {slider[1]} AND prob >= {slider[0]}
                      AND source = {source}
                      AND retention_time_exp < 20
                      AND (validation is null or validation='') 
                      ORDER BY 3 DESC;"""
        df = get_df_full_query(query)
        return df.to_json(date_format='iso', orient='split')


    @app.callback(Output('non-displayed-resultat', 'children'), 
                  [Input('store-results', 'n_clicks')],
                  [State('table-echantillon-resultat', 'data'),
                  State('table-echantillon-resultat', 'columns')])
    def clean_data(n, rows, columns):
        if n is None:
            return('first run')
        df = pd.DataFrame(rows, columns=[c['name'] for c in columns])
        # df = df[['id_mzml', 'id_molecule', 'id_analysis', 'retention_time_exp', 'validation']]
        update_validation(df)
        return('done')


    @app.callback(
        Output('output-container-range-slider', 'children'),
        [Input('my-range-slider', 'value')])
    def update_output(value):
        return f'Score RT entre {value[0]} et {value[1]}'


    @app.callback(
        [Output('analysis-dropdown', 'options'),
        Output('analysis-dropdown', 'value')],
        [Input('non-displayed-resultat', 'children')]
    )
    def update_date_dropdown(name):
        df_analysis = get_df_full_query(f"""SELECT id_analysis FROM public.scores GROUP BY 1 ORDER BY 1""")
        return([{'label': i, 'value': i} for i in df_analysis.id_analysis.values],2)

    @app.callback(
        [Output('file-dropdown', 'options'),
        Output('file-dropdown', 'value')],
        [Input('analysis-dropdown', 'value')]
    )
    def update_date_dropdown(name):
        if name==None or name=='None':
            return([], None)
        elif name!=None and name!='None':
            df_files = get_df_full_query(f"""SELECT mzml_file FROM public.scores where id_analysis = '{name}' GROUP BY 1""")
            # df_files['mzml_file'] = df_files['mzml_file'].apply(lambda x : x[4:])
            return([{'label': i, 'value': i} for i in df_files.mzml_file.values],"None")


    @app.callback(
        [Output("modal", "is_open"),
        Output("modal-header", "children"),
        Output("chromatogram-modal", "figure"),
        Output("Nb_spectrum_value-modal", "children"),
        Output("Acq_mode_value-modal", "children"),
        Output("Ion_mode_value-modal", "children"),
        Output("Mass_value-modal", "children"),
        Output("RT_value-modal", "children"),
        Output("search-in-chromato-modal", "figure"),
        Output('datatable-peaks-modal', 'data'),
        Output("search-fragment-10-only-fragment-modal", "figure"),
        Output("fragment-10-modal", "figure"),
        Output("fragment-10-similarity-modal", "children"),
        Output("fragment-10-similarity-cosine-root-modal", "children"),
        Output("fragment-10-similarity-pearson-modal", "children"),
        Output("fragment-10-similarity-scholle-modal", "children"),
        Output("search-fragment-20-only-fragment-modal", "figure"),
        Output("fragment-20-modal", "figure"),
        Output("fragment-20-similarity-modal", "children"),
        Output("fragment-20-similarity-cosine-root-modal", "children"),
        Output("fragment-20-similarity-pearson-modal", "children"),
        Output("fragment-20-similarity-scholle-modal", "children"),
        Output("search-fragment-40-only-fragment-modal", "figure"),
        Output("fragment-40-modal", "figure"),
        Output("fragment-40-similarity-modal", "children"),
        Output("fragment-40-similarity-cosine-root-modal", "children"),
        Output("fragment-40-similarity-pearson-modal", "children"),
        Output("fragment-40-similarity-scholle-modal", "children"),
        Output("profil-isotopique-experimental-modal", "figure"),
        Output("profil-isotopique-theorique-modal", "figure"),
        Output("isotopic-similarity-modal", "children")],
        [Input("show-results", "n_clicks"), 
        # Input("close", "n_clicks")
        ],
        [State("modal", "is_open"),
        State('intermediate-value-echantillon-resultat', 'children'),
        State('table-echantillon-resultat', "selected_rows")],
    )
    def toggle_modal(n1, is_open, jsonified_cleaned_data, derived_virtual_selected_rows):
        if derived_virtual_selected_rows is None or derived_virtual_selected_rows==[]:
            return(is_open, '', None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)

        #extract meta data
        df = pd.read_json(jsonified_cleaned_data, orient='split')
        df['retention_time_exp'] = df['retention_time_exp'].round(5) 
        id_mzml=[df.id_mzml[df.index==i].values[0] for i in derived_virtual_selected_rows][0]
        id_molecule=[df.id_molecule[df.index==i].values[0] for i in derived_virtual_selected_rows][0]
        id_analysis=[df.id_analysis[df.index==i].values[0] for i in derived_virtual_selected_rows][0]
        retention_time_exp=[df.retention_time_exp[df.index==i].values[0] for i in derived_virtual_selected_rows][0]
        mzml_file=[df.mzml_file[df.index==i].values[0] for i in derived_virtual_selected_rows][0][4:]
        molecule=[df.molecule_name[df.index==i].values[0] for i in derived_virtual_selected_rows][0]
        #modal header
        modal_header = f"""Résultat de recherche de '{molecule}' dans '{mzml_file}'"""
        #read mzml
        fig, spectrum_number, acquisition_mode, ionisation = update_chromato_carac_db(id_mzml)
        # molecule meta data
        df_molecule_m_rt = get_df_full_query(f"""SELECT mass, retention_time FROM public.molecules WHERE id_molecule={id_molecule} ;""")
        try:
            mass = df_molecule_m_rt.mass.values[0]
            RT = df_molecule_m_rt.retention_time.values[0]
        except:
            mass = None
            RT = None
        if RT==None:
            RT = "Nan"
        mass = f"{mass} m/z" 
        RT = f"{RT} min"
        # search mol in mzml
        fig1, peaks_dict = get_search_mass_mzml(id_mzml, id_molecule)
        #fragmentaion 10 ev
        frag_the_10, frag_exp_10, cos_10, root_10, pearson_10, scholle_10 = get_fragment_from_db(id_mzml, id_molecule, id_analysis, retention_time_exp, 10)
        #fragmentaion 20 ev
        frag_the_20, frag_exp_20, cos_20, root_20, pearson_20, scholle_20 = get_fragment_from_db(id_mzml, id_molecule, id_analysis, retention_time_exp, 20)
        #fragmentaion 40 ev
        frag_the_40, frag_exp_40, cos_40, root_40, pearson_40, scholle_40 = get_fragment_from_db(id_mzml, id_molecule, id_analysis, retention_time_exp, 40)
        #isotopic profile
        iso_the, iso_exp, cosine_iso = get_isotopic_profile_from_db(id_mzml, id_molecule, id_analysis, retention_time_exp)

       
        if n1:
            return(not is_open, modal_header, fig, spectrum_number, acquisition_mode, ionisation, mass, RT, fig1, peaks_dict, frag_the_10, frag_exp_10, cos_10, root_10, pearson_10, scholle_10, frag_the_20, frag_exp_20, cos_20, root_20, pearson_20, scholle_20, frag_the_40, frag_exp_40, cos_40, root_40, pearson_40, scholle_40, iso_the, iso_exp, cosine_iso)
        return(is_open, modal_header, fig, spectrum_number, acquisition_mode, ionisation, mass, RT, fig1, peaks_dict, frag_the_10, frag_exp_10, cos_10, root_10, pearson_10, scholle_10, frag_the_20, frag_exp_20, cos_20, root_20, pearson_20, scholle_20, frag_the_40, frag_exp_40, cos_40, root_40, pearson_40, scholle_40, iso_the, iso_exp, cosine_iso)


    @app.callback(
        [Output('source-bdd', 'options'),
        Output('source-bdd', 'value')],
        [Input('analysis-dropdown', 'value')]
    )
    def update_date_dropdown(name):
        if name==None or name=='None':
            return([], None)
        elif name!=None and name!='None':
            df_files = get_df_full_query(f"""SELECT source FROM public.scores where id_analysis = '{name}' GROUP BY 1""")
            # df_files['mzml_file'] = df_files['mzml_file'].apply(lambda x : x[4:])
            return([{'label': i, 'value': i} for i in df_files.source.values],"None")

    # @app.callback(
    #     [Output("search-fragment-10-only-fragment", "figure"),
    #     Output("fragment-10", "figure"),
    #     Output("fragment-10-similarity", "children"),
    #     Output("fragment-10-similarity-cosine-root", "children"),
    #     Output("fragment-10-similarity-pearson", "children"),
    #     Output("fragment-10-similarity-scholle", "children")],
    #     [Input('name-dropdown', 'value'),
    #     Input('name-dropdown-Mol', 'value'),
    #     Input('name-dropdown-Source', 'value'),
    #     Input('name-dropdown-Species', 'value'),
    #     Input('opt-dropdown-spectrum', 'value')]
    # )
    # def fragm_10_only_fragment(name, name_mol, source, species, retention_time_exp):
    #     if name == None or name_mol==None or source==None or species==None or retention_time_exp==None:
    #         fig = go.Figure()
    #         fig.update_layout(
    #             margin=dict(t=0, b=0, r=40, l=40),
    #             height=300,
    #             xaxis_showticklabels=True,
    #             xaxis_title='m/z'
    #         )
    #         return fig, fig, "", "", "", ""  
    #     return(get_fragment_from_db(name, name_mol, source, species, retention_time_exp, 10))


    # @app.callback([Output('selected-row-ids-echantillon-test-resultat', 'children'),
    #               Output('table-echantillon-resultat', 'selected_rows')],
    #               [Input('confirm-resultat', 'submit_n_clicks')],
    #               [State('intermediate-value-echantillon-resultat', 'children'),
    #               State('table-echantillon-resultat', "selected_rows"),
    #               State('threshold-positif-resultat', 'value'),
    #               State('threshold-negatif-resultat', 'value'),
    #               State('molecule-bdd-resultat', 'value')])
    # def update_output(n, jsonified_cleaned_data, derived_virtual_selected_rows, pos, neg, value):
        # if derived_virtual_selected_rows is None or derived_virtual_selected_rows==[] or value is None or value==[]:
        #     return(html.Div(), [])

    #     df = pd.read_json(jsonified_cleaned_data, orient='split')
    #     mzml_files=[df.mzml_file[df.index==i].values[0] for i in derived_virtual_selected_rows]
    #     if len(mzml_files)!=0:
    #         launch_analysis(str(pos), str(neg), value, mzml_files)
    #     children = html.Div(
    #                     [html.P('Analyse lancée sur :')]+
    #                     [html.P(df.mzml_file[df.index==i].values[0]) for i in derived_virtual_selected_rows]+
    #                     [html.P('avec un threshold positif de')]+
    #                     [html.P(pos)]+
    #                     [html.P('avec un threshold negatif de')]+
    #                     [html.P(neg)]+
    #                     [html.P('avec les BDDs')]+
    #                     [html.P(str(value))]
    #                 )
    #     return(children, [])