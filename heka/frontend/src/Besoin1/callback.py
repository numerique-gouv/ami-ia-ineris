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
# smoe helper functions
from Besoin1.helpers import *


# Folder that contains all mzml files and that after each deployment get synchronized with GS bucket
FILE_PATH_BASE = '/heka/storage/'

# INERIS database stored in our postgres
df = get_df_full_query("""SELECT * FROM public.ineris_bdd""")
# function from helpers that list all blobs in the storage bucket
blobs = list_blobs()


# Function to call all callbacks 
def register_callbacks(app):
    @app.callback(
        [Output("chromatogram", "figure"),
        Output("Nb_spectrum_value", "children"),
        Output("Acq_mode_value", "children"),
        Output("Ion_mode_value", "children")],
        [Input('name-dropdown', 'value')]
    )
    def chromato(mzml_file):
        # If the dropdown in none we don't launch any computation
        if mzml_file == None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                xaxis_showticklabels=True,
                xaxis_title='Time (min)'
            )
            return fig, None, None, None
        return(update_chromato_carac_db(mzml_file))



    @app.callback(
        [Output('name-dropdown-Source', 'options'),
        Output('name-dropdown-Source', 'value')],
        [Input('name-dropdown-Mol', 'value')]
    )
    def update_date_dropdown(name):
        if name == None:
            return([],None)
        df_source = get_df_full_query(f"""SELECT source FROM public.molecules WHERE molecule_name='{name}' GROUP BY 1""")
        return([{'label': i, 'value': i} for i in df_source.source.values],"None")


    @app.callback(
        [Output('name-dropdown-Species', 'options'),
        Output('name-dropdown-Species', 'value')],
        [Input('name-dropdown-Mol', 'value'),
        Input('name-dropdown-Source', 'value')]
    )
    def update_date_dropdown(name, source):
        if name == None or source == None:
            return([],None)
        df_species = get_df_full_query(f"""SELECT species FROM public.molecules WHERE molecule_name='{name}' AND source='{source}' GROUP BY 1""")
        return([{'label': i, 'value': i} for i in df_species.species.values],None)



    @app.callback(
        [Output("Mass_value", "children"),
        Output("RT_value", "children")],
        [Input('name-dropdown-Mol', 'value'),
        Input('name-dropdown-Source', 'value'),
        Input('name-dropdown-Species', 'value')]
    )
    def set_mass(name, source, species):
        if name==None or source==None or species==None:
            return None, None
        # get mass and RT from BDD
        df_molecule_m_rt = get_df_full_query(f"""SELECT mass, retention_time FROM public.molecules WHERE molecule_name='{name}' AND source='{source}' AND species='{species}'""")
        try:
            mass = df_molecule_m_rt.mass.values[0]
            RT = df_molecule_m_rt.retention_time.values[0]
        except:
            return None, None
        if RT==None:
            RT = "Nan"
        return f"{mass} m/z", f"{RT} min"



    @app.callback(
        [Output("search-in-chromato", "figure"),
        Output('datatable-peaks', 'data')],
        [Input('name-dropdown', 'value'),
        Input('name-dropdown-Mol', 'value'),
        Input('name-dropdown-Source', 'value'),
        Input('name-dropdown-Species', 'value')]
    )
    def search_in_chromato(name, name_mol, source, species):
        if name == None or name_mol==None or source==None or species==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                xaxis_showticklabels=True,
                xaxis_title='m/z'
            )
            return fig, []
        return(get_search_mass_mzml(name, name_mol, source, species))


    @app.callback(
        Output('opt-dropdown-spectrum', 'options'),
        [Input('name-dropdown', 'value'),
        Input('name-dropdown-Mol', 'value'),
        Input('name-dropdown-Source', 'value'),
        Input('name-dropdown-Species', 'value')]
    )
    def update_date_dropdown(name, name_mol, source, species):
        if name == None or name_mol==None or source==None or species==None:
            return([])
        mzml_file_charc = get_mzml_charc(name.replace('/','\\'))
        molecul_charc = get_molecule_charc(name_mol, source, species)
        id_mzml = mzml_file_charc.id_mzml.values[0]
        ionisation = mzml_file_charc.ionisation.values[0]
        id_molecule = molecul_charc.id_molecule.values[0]
        query_peaks=f"""SELECT retention_time_exp FROM public.extracted_peaks WHERE id_mzml = {id_mzml} AND id_molecule = {id_molecule} AND tic>10000 ORDER BY 1;""" if ionisation=='POS' else f"""SELECT retention_time_exp, tic, mass_exp FROM public.extracted_peaks WHERE id_mzml = {id_mzml} AND id_molecule = {id_molecule} ORDER BY 1;""" 
        df_peaks = get_df_full_query(query_peaks)
        if len(df_peaks)==0:
            return([])
        return [{'label': i, 'value': i} for i in df_peaks.retention_time_exp.values]







    @app.callback(
        [Output("search-fragment-10-only-fragment", "figure"),
        Output("fragment-10", "figure"),
        Output("fragment-10-similarity", "children"),
        Output("fragment-10-similarity-cosine-root", "children"),
        Output("fragment-10-similarity-pearson", "children"),
        Output("fragment-10-similarity-scholle", "children")],
        [Input('name-dropdown', 'value'),
        Input('name-dropdown-Mol', 'value'),
        Input('name-dropdown-Source', 'value'),
        Input('name-dropdown-Species', 'value'),
        Input('opt-dropdown-spectrum', 'value')]
    )
    def fragm_10_only_fragment(name, name_mol, source, species, retention_time_exp):
        if name == None or name_mol==None or source==None or species==None or retention_time_exp==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                xaxis_showticklabels=True,
                xaxis_title='m/z'
            )
            return fig, fig, "", "", "", ""  
        return(get_fragment_from_db(name, name_mol, source, species, retention_time_exp, 10))



    @app.callback(
        [Output("search-fragment-20-only-fragment", "figure"),
        Output("fragment-20", "figure"),
        Output("fragment-20-similarity", "children"),
        Output("fragment-20-similarity-cosine-root", "children"),
        Output("fragment-20-similarity-pearson", "children"),
        Output("fragment-20-similarity-scholle", "children")],
        [Input('name-dropdown', 'value'),
        Input('name-dropdown-Mol', 'value'),
        Input('name-dropdown-Source', 'value'),
        Input('name-dropdown-Species', 'value'),
        Input('opt-dropdown-spectrum', 'value')]
    )
    def fragm_10_only_fragment(name, name_mol, source, species, retention_time_exp):
        if name == None or name_mol==None or source==None or species==None or retention_time_exp==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                xaxis_showticklabels=True,
                xaxis_title='m/z'
            )
            return fig, fig, "", "", "", ""  
        return(get_fragment_from_db(name, name_mol, source, species, retention_time_exp, 20))


    @app.callback(
        [Output("search-fragment-40-only-fragment", "figure"),
        Output("fragment-40", "figure"),
        Output("fragment-40-similarity", "children"),
        Output("fragment-40-similarity-cosine-root", "children"),
        Output("fragment-40-similarity-pearson", "children"),
        Output("fragment-40-similarity-scholle", "children")],
        [Input('name-dropdown', 'value'),
        Input('name-dropdown-Mol', 'value'),
        Input('name-dropdown-Source', 'value'),
        Input('name-dropdown-Species', 'value'),
        Input('opt-dropdown-spectrum', 'value')]
    )
    def fragm_10_only_fragment(name, name_mol, source, species, retention_time_exp):
        if name == None or name_mol==None or source==None or species==None or retention_time_exp==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                xaxis_showticklabels=True,
                xaxis_title='m/z'
            )
            return fig, fig, "", "", "", ""  
        return(get_fragment_from_db(name, name_mol, source, species, retention_time_exp, 40))



    @app.callback(
        [Output("profil-isotopique-experimental", "figure"),
        Output("profil-isotopique-theorique", "figure"),
        Output("isotopic-similarity", "children")],
        [Input('name-dropdown', 'value'),
        Input('name-dropdown-Mol', 'value'),
        Input('name-dropdown-Source', 'value'),
        Input('name-dropdown-Species', 'value'),
        Input('opt-dropdown-spectrum', 'value')]
    )
    def spectru(name, name_mol, source, species, retention_time_exp):
        if name == None or name_mol==None or source==None or species==None or retention_time_exp==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                xaxis_showticklabels=True,
                xaxis_title='m/z'
            )
            return fig, fig, ""
        return(get_isotopic_profile_from_db(name, name_mol, source, species, retention_time_exp))



    @app.callback(
        Output('name-dropdown-Mol', 'value'),
        [Input('name-dropdown', 'value')]
    )
    def update_date_dropdown(name):
        return(None)

    @app.callback(
        Output('opt-dropdown-spectrum', 'value'),
        [Input('name-dropdown', 'value'),
        Input('name-dropdown-Mol', 'value')]
    )
    def update_date_dropdown(name, name_mol):
        return(None)