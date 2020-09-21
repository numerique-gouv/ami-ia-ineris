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
        Output("Nb_spectrum_value", "children")],
        [Input('name-dropdown', 'value')]
    )
    def chromato(name):
        # If the dropdown in none we don't launch any computation
        if name == None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                xaxis_showticklabels=True,
                xaxis_title='m/z'
            )
            return fig, None

        # We look for the mzml file in the appropriate folder 
        name = [i['blob_name'] for i in blobs if name in i['blob_name']][0]
        # Read and compute chromatograph from mzml using pymzml
        mzml_file = FILE_PATH_BASE + name
        run = pymzml.run.Reader(mzml_file)
        # juste to get n which is the number of spectrums
        for n,spec in enumerate(run):
            continue
        mzml_basename = os.path.basename(mzml_file)
        pf = pymzml.plot.Factory()
        pf.new_plot()
        pf.add(run["TIC"].peaks(), color=(0, 0, 0), style="lines", title=mzml_basename)
        X = list(pf.plots[0][0].x)
        Y = list(pf.plots[0][0].y)
        #################################################
        # Create figure object to show the chromatograph
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=X,
                y=Y,
                mode="lines",
                name="Chromatogram",
                line=dict(color="rgb(150, 200, 250)"),
                showlegend=False,
            )
        )
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='Retention Time (min)',
            yaxis_title='TIC'
        )
        return fig,n


    @app.callback(
        Output("Acq_mode_value", "children"),
        [Input("name-dropdown", "value")],
    )
    def set_acq_mode(name):
        if name == None:
            return None 
        if 'allion' in name:
            return('Data independant')
        if 'MSMS' in name:
            return('Data dependant')

    @app.callback(
        Output("Ion_mode_value", "children"),
        [Input("name-dropdown", "value")],
    )
    def set_ion_mode(name):
        if name == None:
            return None
        # name = [i['blob_name'] for i in blobs if name in i['blob_name']][0]
        # mzml_file = FILE_PATH_BASE + name
        # run = pymzml.run.Reader(mzml_file)
        # for spec in run:
        #     break
        if name.split('/')[-2]=='NEG':
            ionisation = 'Negative ionisation'
        if name.split('/')[-2]=='POS':
            ionisation = 'Positive ionisation'
        return(ionisation)


    @app.callback(
        Output('opt-dropdown-spectrum', 'options'),
        [Input('name-dropdown', 'value')]
    )
    def update_date_dropdown(name):
        if name == None:
            return([])
        name = [i['blob_name'] for i in blobs if name in i['blob_name']][0]
        # get and create labels for all spectrums within an mzml file
        fnameDict = get_mzml_values(name)
        return [{'label': i, 'value': i} for i in fnameDict if (re.search(r'of (.*?) eV', i).group(1) == '0')]


    @app.callback(
        [Output("Mass_value", "children"),
        Output("RT_value", "children")],
        [Input("name-dropdown-Mol", "value")],
    )
    def set_mass(name):
        if name==None:
            return None, None
        # get mass and RT from BDD
        df1 = df[df['Name']==name]
        mass = df1.values[0][2]
        RT = df1.values[0][3]
        return f"{mass} m/z", f"{RT} min"



    @app.callback(
        Output("fragment-10", "figure"),
        [Input('name-dropdown', 'value'),
        Input('name-dropdown-Mol', 'value')]
    )
    def fragm_10(name, name_mol):
        if name == None or name_mol==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                xaxis_showticklabels=True,
                xaxis_title='m/z'
            )
            return fig
        # name = [i['blob_name'] for i in blobs if name in i['blob_name']][0]
        # mzml_file = FILE_PATH_BASE + name
        # run = pymzml.run.Reader(mzml_file)
        # for spec in run:
        #     break
        if name.split('/')[-2]=='NEG':
            ionisation = 'Negative'
        if name.split('/')[-2]=='POS':
            ionisation = 'Positive'

        collision_energy = 10

        df1 = df[(df['Name']==name_mol) & (df['Ion Polarity']==ionisation) & (df['Collision Energy']==collision_energy)]

        # All masses of fragments of the choosen molecule in the choosen ionisation and the choosen collision energy
        X = df1.T.values[-2]
        # All intensities of fragments of the choosen molecule in the choosen ionisation and the choosen collision energy
        Y = df1.T.values[-1]

        # We choosed to show x,y instead of X, Y in order to have a spectrum plot
        x=[]
        y=[]
        for i in range(len(X)):
            x.append(X[i])
            x.append(X[i])
            x.append(X[i])
            x.append(None)
            y.append(0.0)
            y.append(Y[i])
            y.append(0.0)
            y.append(None)

        # Create figure object to be shown
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name="Fragmentation 10 eV",
                marker_color="rgb(150, 200, 250)",
                showlegend=False,
            )
        )
        # get molecule mass in order to show only a shoosen range of masses
        mass = df[df['Name']==name_mol].values[0][2]
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z',
            yaxis_title='Relative intensity',
            xaxis = dict(range=[0,mass+2])
        )
        return fig


    @app.callback(
        Output("fragment-20", "figure"),
        [Input('name-dropdown', 'value'),
        Input('name-dropdown-Mol', 'value')]
    )
    def fragm_20(name, name_mol):
        if name == None or name_mol==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                xaxis_showticklabels=True,
                xaxis_title='m/z'
            )
            return fig
        # name = [i['blob_name'] for i in blobs if name in i['blob_name']][0]
        # mzml_file = FILE_PATH_BASE + name
        # run = pymzml.run.Reader(mzml_file)
        # for spec in run:
        #     break
        if name.split('/')[-2]=='NEG':
            ionisation = 'Negative'
        if name.split('/')[-2]=='POS':
            ionisation = 'Positive'

        collision_energy = 20

        df1 = df[(df['Name']==name_mol) & (df['Ion Polarity']==ionisation) & (df['Collision Energy']==collision_energy)]


        # All masses of fragments of the choosen molecule in the choosen ionisation and the choosen collision energy
        X = df1.T.values[-2]
        # All intensities of fragments of the choosen molecule in the choosen ionisation and the choosen collision energy
        Y = df1.T.values[-1]

        # We choosed to show x,y instead of X, Y in order to have a spectrum plot
        x=[]
        y=[]
        for i in range(len(X)):
            x.append(X[i])
            x.append(X[i])
            x.append(X[i])
            x.append(None)
            y.append(0.0)
            y.append(Y[i])
            y.append(0.0)
            y.append(None)

        # Create figure object to be shown
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name="Fragmentation 20 eV",
                marker_color="rgb(150, 200, 250)",
                showlegend=False,
            )
        )
        # get molecule mass in order to show only a shoosen range of masses
        mass = df[df['Name']==name_mol].values[0][2]
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z',
            yaxis_title='Relative intensity',
            xaxis = dict(range=[0,mass+2])
        )
        return fig

    @app.callback(
        Output("fragment-40", "figure"),
        [Input('name-dropdown', 'value'),
        Input('name-dropdown-Mol', 'value')]
    )
    def fragm_40(name, name_mol):
        if name == None or name_mol==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                xaxis_showticklabels=True,
                xaxis_title='m/z'
            )
            return fig
        # name = [i['blob_name'] for i in blobs if name in i['blob_name']][0]
        # mzml_file = FILE_PATH_BASE + name
        # run = pymzml.run.Reader(mzml_file)
        # for spec in run:
        #     break
        if name.split('/')[-2]=='NEG':
            ionisation = 'Negative'
        if name.split('/')[-2]=='POS':
            ionisation = 'Positive'

        collision_energy = 40

        df1 = df[(df['Name']==name_mol) & (df['Ion Polarity']==ionisation) & (df['Collision Energy']==collision_energy)]


        # All masses of fragments of the choosen molecule in the choosen ionisation and the choosen collision energy
        X = df1.T.values[-2]
        # All intensities of fragments of the choosen molecule in the choosen ionisation and the choosen collision energy
        Y = df1.T.values[-1]

        # We choosed to show x,y instead of X, Y in order to have a spectrum plot
        x=[]
        y=[]
        for i in range(len(X)):
            x.append(X[i])
            x.append(X[i])
            x.append(X[i])
            x.append(None)
            y.append(0.0)
            y.append(Y[i])
            y.append(0.0)
            y.append(None)


        # Create figure object to be shown
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name="Fragmentation 40 eV",
                marker_color="rgb(150, 200, 250)",
                showlegend=False,
            )
        )
        # get molecule mass in order to show only a shoosen range of masses
        mass = df[df['Name']==name_mol].values[0][2]
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z',
            yaxis_title='Relative intensity',
            xaxis = dict(range=[0,mass+2])
        )
        return fig

    @app.callback(
        [Output("search-in-chromato", "figure"),
        Output(component_id='datatable-peaks', component_property='data')],
        [Input('name-dropdown', 'value'),
        Input('name-dropdown-Mol', 'value')]
    )
    def search_in_chromato(name, name_mol):
        if name == None or name_mol==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                xaxis_showticklabels=True,
                xaxis_title='m/z'
            )
            return fig, []   
        # get data for the choosen molecule
        df1 = df[df['Name']==name_mol]
        m = df1.values[0][2]
        rt = df1.values[0][3]
        # read mzml file
        name = [i['blob_name'] for i in blobs if name in i['blob_name']][0]
        mzml_file = FILE_PATH_BASE + name
        run = pymzml.run.Reader(mzml_file)

        # creation of a list that contains for each spectrum its scan time and also the TIC for the mass to look for with an error of 0.002
        L=[]
        for n, spec in enumerate(run):
            if spec['collision energy'] == None:
                if name.split('/')[-2]=='NEG':
                    # when the isonisation is negative we look for mass m-1.00728
                    spec_tronc = spec.reduce(mz_range=(m-0.002-1.00728,m+0.002-1.00728)).tolist()
                elif name.split('/')[-2]=='POS':
                    # when the ionisation is positive we look for mass m+1.00728
                    spec_tronc = spec.reduce(mz_range=(m-0.002+1.00728,m+0.002+1.00728)).tolist()
                I = sum([i[1] for i in spec_tronc])
                L.append([spec.scan_time_in_minutes(), I])

        # X is a list of all scans time and Y a list of TICs 
        X = [i[0] for i in L]
        Y = [i[1] for i in L]
        # A rectangle that shows tolerance on retention time (0.2 min tolerance)
        Z = [max([i[1] for i in L]) if ((i[0]<=rt+0.2) & (i[0]>=rt-0.2)) else 0 for i in L]

        # extract peaks that corresponds to retention times when the mass that we look for exists the most
        # We use two parameters which are prominence of 10000 which means that the difference between intensities of 
        # two close pics should be greater than 10000 and a distance of 20 which means that peaks should be enough distanciated
        peaks, _ = find_peaks(Y, prominence=10000, distance=20)
        X_peaks = np.array(X)[peaks]
        Y_peaks = np.array(Y)[peaks] 
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=X,
                y=Y,
                mode="lines",
                name=f'TIC for mass {m}',
                line=dict(color="rgb(100, 150, 200)"),
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=X,
                y=Z,
                mode="lines",
                name='Theoretical RT',
                line=dict(color="rgb(150, 200, 250)"),
                showlegend=False,
            )
        )
        fig.add_trace(
            go.Scatter(
                x=X_peaks,
                y=Y_peaks,
                mode="markers",
                name='Apex',
                line=dict(color="rgb(255, 0, 0)"),
                showlegend=False,
            )
        )
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='Retention Time (min)',
            yaxis_title='TIC'
        )
        peaks_dict = [{"Minute" : X_peaks[i], "Peak value" : Y_peaks[i]} for i,j in enumerate(X_peaks)]
        return fig, peaks_dict



    @app.callback(
        [Output("scan-spectrum", "figure"),
        Output("profil-isotopique-experimental", "figure"),
        Output("profil-isotopique-theorique", "figure"),
        Output("isotopic-similarity", "children")],
        [Input('name-dropdown', 'value'),
        Input('opt-dropdown-spectrum', 'value'),
        Input('name-dropdown-Mol', 'value')]
    )
    def spectru(name, id2, name_mol):
        if name == None or id2==None or name_mol==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                xaxis_showticklabels=True,
                xaxis_title='m/z'
            )
            return fig, fig, fig, ""
        # read mzlm 
        name = [i['blob_name'] for i in blobs if name in i['blob_name']][0]
        mzml_file = FILE_PATH_BASE + name
        run = pymzml.run.Reader(mzml_file)
        mzml_basename = os.path.basename(mzml_file)
        # get spectrum id and retention time
        try:
            spec_id = re.search(r'spectrum (.*?) at', id2).group(1)
            spec = run[int(spec_id)]
        except:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                xaxis_showticklabels=True,
                xaxis_title='m/z'
            )
            return(fig, fig, fig, "")
        # get spectrum of the extracted id
        p = pymzml.plot.Factory()
        p.new_plot()
        p.add(spec.peaks("centroided"), color=(0, 0, 0), style="sticks", name="peaks")
        X = list(p.plots[0][0].x)
        Y = list(p.plots[0][0].y)
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(
                x=X,
                y=Y,
                mode="lines",
                name=f"Spectrum with energy collision of {get_colision_energy(spec)} eV",
                line=dict(color="rgb(150, 200, 250)"),
                showlegend=False,
            )
        )
        fig1.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z'
        )

        # get formula and use get_compo from helpers to transform string formula to dictionary
        Formula = df[df['Name']==name_mol]['Formula'].values[0]
        mol = get_compo(Formula)

        if name.split('/')[-2]=='NEG':
            charge = -1
        if name.split('/')[-2]=='POS':
            charge = 1


        # use brainpy to generate theoric isotopic profile
        theoretical_isotopic_cluster = isotopic_variants(mol, npeaks=10, charge=charge)
        X1 = [peak.mz for peak in theoretical_isotopic_cluster]
        Y1 = [peak.intensity for peak in theoretical_isotopic_cluster]
        # normalize to have profil with percentage
        Y1 = [100*y/max(Y1) for y in Y1]

        # we get rid of all pics that are under 0.1%
        indexes = []
        for indx,perc in enumerate(Y1):
            if perc < 0.1:
                indexes.append(indx)
        for index in sorted(indexes, reverse=True):
            del X1[index]
            del Y1[index]

        x=[]
        y=[]
        for i in range(len(X1)):
            x.append(X1[i])
            x.append(X1[i])
            x.append(X1[i])
            x.append(X1[i])
            y.append(0.0)
            y.append(Y1[i])
            y.append(0.0)
            y.append(None) 

        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name="Isotopic profile",
                line=dict(color="rgb(150, 200, 250)"),
                showlegend=False,
            )
        )
        fig2.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z',
            yaxis_title='Relative intensity',
            xaxis = dict(range=[min(X1)-1,max(X1)+1])
        )

        mass = df[df['Name']==name_mol].values[0][2]
        # Get only the part of spectrum that contains isotopic profile
        if charge == 1:
            spec_tronc = spec.reduce(mz_range=(mass,mass+11))
        elif charge == -1:
            spec_tronc = spec.reduce(mz_range=(mass-2,mass+9))

        # Signal alignment
        X = [i[0] for i in spec_tronc for j in X1 if abs(i[0]-j)<=0.003]
        Y = [i[1] for i in spec_tronc for j in X1 if abs(i[0]-j)<=0.003]
        try:
            Y = 100 * np.array(Y)/max(Y)
        except:
            pass
        x=[]
        y=[]
        for i in range(len(X)):
            x.append(X[i])
            x.append(X[i])
            x.append(X[i])
            x.append(X[i])
            y.append(0.0)
            y.append(Y[i])
            y.append(0.0)
            y.append(None)        
        fig3 = go.Figure()
        fig3.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name=f"Profil isotopique expérimental",
                showlegend=False,
            )
        )
        fig3.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z',
            xaxis = dict(range=[min(X1)-1,max(X1)+1])
        )

        X_ = []
        Y_ = []
        for i,j in enumerate(X1):
            L=[]
            for k,l in enumerate(X):
                if abs(j-l)<=0.003:
                    L.append([abs(j-l),Y[k]])
            X_.append(j)
            # If we dont find any pic in experimental profile we put 0 as intensity for this mass
            if len(L)==0:
                Y_.append(0)
            # if we find more than one pic we take the closest pic in m/z
            else:
                min_couple = 1
                min_index = 0
                for index_couple, couple in enumerate(L):
                    if couple[0]<min_couple:
                        min_couple = couple[0]
                        min_index = index_couple
                Y_.append(L[min_index][1])

        #if Y_ contains only one pic of 100% we compare all the vectors
        if [i for i in Y_ if i>0.1]==[100]:
            cosine_sim = 1 - spatial.distance.cosine(Y1, Y_)
        #if Y_ is a nulle vector return 0
        elif [i for i in Y_ if i!=0]==[]:
            cosine_sim = 0
        # elif we dont take into account the first pic of 100%
        else:
            cosine_sim = 1 - spatial.distance.cosine(Y1[1:], Y_[1:])

        return fig1, fig3, fig2, cosine_sim


    @app.callback(
        [Output("search-fragment-10", "figure"),
        Output("search-fragment-10-only-fragment", "figure"),
        Output("fragment-10-similarity", "children"),
        Output("fragment-10-similarity-cosine-root", "children"),
        Output("fragment-10-similarity-pearson", "children"),
        Output("fragment-10-similarity-scholle", "children")],
        [Input('name-dropdown', 'value'),
        Input('name-dropdown-Mol', 'value'),
        Input('opt-dropdown-spectrum', 'value')]
    )
    def fragm_10_only_fragment(name, name_mol, id2):
        if name == None or id2==None or name_mol==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                xaxis_showticklabels=True,
                xaxis_title='m/z'
            )
            return fig, fig, "", "", "", ""  
        name = [i['blob_name'] for i in blobs if name in i['blob_name']][0]
        mzml_file = FILE_PATH_BASE + name
        run = pymzml.run.Reader(mzml_file)

        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z'
        )
        # get mode in name
        mode = 'Data independant' if ('allion' in name) else 'Data dependant'

        # There in no 10ev fragmentation in data independant mode
        if mode == 'Data independant':
            return fig, fig, "", "", "", ""

        # get id of spec and its energy
        try:
            spec_id = re.search(r'spectrum (.*?) ', id2).group(1)
            spec_ev = re.search(r'of (.*?) eV', id2).group(1)        
        except:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                xaxis_showticklabels=True,
                xaxis_title='m/z'
            )
            return fig, fig, "", "", "", ""

        # this small script gets the following spec after the scan
        flag_out = -1
        for spec in run:
            if flag_out == 0 and spec['collision energy'] == 10.0:
                break
            if spec.ID == int(spec_id):
                flag_out = 1
            flag_out += -1


        p = pymzml.plot.Factory()
        p.new_plot()
        p.add(spec.peaks("centroided"), color=(0, 0, 0), style="sticks", name="peaks")
        X = list(p.plots[0][0].x)
        Y = list(p.plots[0][0].y)
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(
                x=X,
                y=Y,
                mode="lines",
                name=f"Spectrum with energy collision of {get_colision_energy(spec)} eV",
                line=dict(color="rgb(150, 200, 250)"),
                showlegend=False,
            )
        )
        mass = df[df['Name']==name_mol].values[0][2]
        fig1.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z',
            yaxis_title='Relative intensity',
            xaxis = dict(range=[0,mass+2])
        )


        if name.split('/')[-2]=='NEG':
            ionisation = 'Negative'
        if name.split('/')[-2]=='POS':
            ionisation = 'Positive'

        collision_energy = 10

        df1 = df[(df['Name']==name_mol) & (df['Ion Polarity']==ionisation) & (df['Collision Energy']==collision_energy)]
        fragment_masses = df1.T.values[-2]
        try:
            m_max = max(fragment_masses)
        except:
            return fig, fig, "", "", "", ""

        tup1 = spec.peaks('centroided').tolist()
        tup2 = spec.peaks('centroided').tolist()

        # let only fragment masses
        for i in tup1:
            for m in fragment_masses:
                min_m = m-0.002
                max_m = m+0.002
                if i[0] > min_m and i[0] < max_m:
                    i[1]=0

        # transform into arrays
        I1 = np.array([I[1] for I in tup1])
        I2 = np.array([I[1] for I in tup2])
        I = I2 - I1
        I_max = np.max(I)
        m_z = np.array([I[0] for I in tup1])


        X = [i for i in m_z.tolist() if i<m_max+1]
        Y = (I * 100 / I_max).tolist()[:len(X)]
        x=[]
        y=[]
        for i in range(len(X)):
            x.append(X[i])
            x.append(X[i])
            x.append(X[i])
            x.append(None)
            y.append(0.0)
            y.append(Y[i])
            y.append(0.0)
            y.append(None)
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name="Fragmentation 10 eV",
                line=dict(color="rgb(150, 200, 250)"),
                showlegend=False,
            )
        )
        fig2.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z',
            yaxis_title='Relative intensity',
            xaxis = dict(range=[0,mass+2])
        )


        base_X = df1.T.values[-2].tolist()
        base_Y = df1.T.values[-1].tolist()


        X_, Y_ = [], []
        for i,j in enumerate(base_X):
            L=[]
            for k,l in enumerate(X):
                if abs(j-l)<=0.003:
                    L.append([abs(j-l),Y[k]])
            X_.append(j)
            # If we dont find any pic in experimental profile we put 0 as intensity for this mass
            if len(L)==0:
                Y_.append(0)
            # if we find more than one pic we take the closest pic in m/z
            else:
                min_couple = 1
                min_index = 0
                for index_couple, couple in enumerate(L):
                    if couple[0]<min_couple:
                        min_couple = couple[0]
                        min_index = index_couple
                Y_.append(L[min_index][1])

        base_Y_root = np.power(np.array(base_Y),.5).tolist()
        Y_root = np.power(np.array(Y_),.5).tolist()
        base_Y_scholle = np.array(base_X)*np.array(base_Y)
        Y_scholle = np.array(base_X)*np.array(Y_)

        cosine_sim = 1 - spatial.distance.cosine(base_Y, Y_)
        cosine_sim_root = 1 - spatial.distance.cosine(base_Y_root, Y_root)
        pearson_sim = 1 - spatial.distance.correlation(base_Y, Y_)
        scholle_sim = 1 - spatial.distance.cosine(base_Y_scholle, Y_scholle)

        return fig1, fig2, str(cosine_sim), str(cosine_sim_root), str(pearson_sim), str(scholle_sim)


    @app.callback(
        [Output("search-fragment-20", "figure"),
        Output("search-fragment-20-only-fragment", "figure"),
        Output("fragment-20-similarity", "children"),
        Output("fragment-20-similarity-cosine-root", "children"),
        Output("fragment-20-similarity-pearson", "children"),
        Output("fragment-20-similarity-scholle", "children")],
        [Input('name-dropdown', 'value'),
        Input('name-dropdown-Mol', 'value'),
        Input('opt-dropdown-spectrum', 'value')]
    )
    def fragm_20_only_fragment(name, name_mol, id2):
        if name == None or id2==None or name_mol==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                # xaxis_tickformat="%d %B (%a)\n%H:%M",
                xaxis_showticklabels=True,
                xaxis_title='m/z'
            )
            return fig , fig, "", "", "", ""
    ##############################################3
        name = [i['blob_name'] for i in blobs if name in i['blob_name']][0]
        mzml_file = FILE_PATH_BASE + name
        run = pymzml.run.Reader(mzml_file)

        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z'
        )

        # get mode in name
        mode = 'Data independant' if ('allion' in name) else 'Data dependant'

        # get id of spec and its energy
        try:
            spec_id = re.search(r'spectrum (.*?) ', id2).group(1)
            spec_ev = re.search(r'of (.*?) eV', id2).group(1)        
        except:
            return fig, fig, "", "", "", ""

        # this small script gets the following spec after the scan
        flag_out = -1
        for spec in run:
            if flag_out == 0 and spec['collision energy'] == 20.0:
                break
            if spec.ID == int(spec_id):
                flag_out = 1 if (mode == 'Data independant') else 2     # in independant mode there is no 10ev collision energy
            flag_out += -1

        p = pymzml.plot.Factory()
        p.new_plot()
        p.add(spec.peaks("centroided"), color=(0, 0, 0), style="sticks", name="peaks")
        X = list(p.plots[0][0].x)
        Y = list(p.plots[0][0].y)
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(
                x=X,
                y=Y,
                mode="lines",
                name=f"Spectrum with energy collision of {get_colision_energy(spec)} eV",
                line=dict(color="rgb(150, 200, 250)"),
                showlegend=False,
            )
        )
        mass = df[df['Name']==name_mol].values[0][2]
        fig1.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z',
            yaxis_title='Relative intensity',
            xaxis = dict(range=[0,mass+2])
        )


        if name.split('/')[-2]=='NEG':
            ionisation = 'Negative'
        if name.split('/')[-2]=='POS':
            ionisation = 'Positive'

        collision_energy = 20

        df1 = df[(df['Name']==name_mol) & (df['Ion Polarity']==ionisation) & (df['Collision Energy']==collision_energy)]
        fragment_masses = df1.T.values[-2]
        try:
            m_max = max(fragment_masses)
        except:
            return fig, fig, "", "", "", ""

        tup1 = spec.peaks('centroided').tolist()
        tup2 = spec.peaks('centroided').tolist()

        for i in tup1:
            for m in fragment_masses:
                min_m = m-0.002
                max_m = m+0.002
                if i[0] > min_m and i[0] < max_m:
                    i[1]=0

        I1 = np.array([I[1] for I in tup1])
        I2 = np.array([I[1] for I in tup2])
        I = I2 - I1
        I_max = np.max(I)
        m_z = np.array([I[0] for I in tup1])


        X = [i for i in m_z.tolist() if i<m_max+1]
        Y = (I * 100 / I_max).tolist()[:len(X)]
        x=[]
        y=[]
        for i in range(len(X)):
            x.append(X[i])
            x.append(X[i])
            x.append(X[i])
            x.append(None)
            y.append(0.0)
            y.append(Y[i])
            y.append(0.0)
            y.append(None)
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name="Fragmentation 10 eV",
                line=dict(color="rgb(150, 200, 250)"),
                showlegend=False,
            )
        )
        fig2.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z',
            yaxis_title='Relative intensity',
            xaxis = dict(range=[0,mass+2])
        )


        base_X = df1.T.values[-2].tolist()
        base_Y = df1.T.values[-1].tolist()

        X_, Y_ = [], []
        for i,j in enumerate(base_X):
            L=[]
            for k,l in enumerate(X):
                if abs(j-l)<=0.003:
                    L.append([abs(j-l),Y[k]])
            X_.append(j)
            # If we dont find any pic in experimental profile we put 0 as intensity for this mass
            if len(L)==0:
                Y_.append(0)
            # if we find more than one pic we take the closest pic in m/z
            else:
                min_couple = 1
                min_index = 0
                for index_couple, couple in enumerate(L):
                    if couple[0]<min_couple:
                        min_couple = couple[0]
                        min_index = index_couple
                Y_.append(L[min_index][1])

        base_Y_root = np.power(np.array(base_Y),.5).tolist()
        Y_root = np.power(np.array(Y_),.5).tolist()
        base_Y_scholle = np.array(base_X)*np.array(base_Y)
        Y_scholle = np.array(base_X)*np.array(Y_)

        cosine_sim = 1 - spatial.distance.cosine(base_Y, Y_)
        cosine_sim_root = 1 - spatial.distance.cosine(base_Y_root, Y_root)
        pearson_sim = 1 - spatial.distance.correlation(base_Y, Y_)
        scholle_sim = 1 - spatial.distance.cosine(base_Y_scholle, Y_scholle)

        return fig1, fig2, str(cosine_sim), str(cosine_sim_root), str(pearson_sim), str(scholle_sim)
    ###############################################################3


    @app.callback(
        [Output("search-fragment-40", "figure"),
        Output("search-fragment-40-only-fragment", "figure"),
        Output("fragment-40-similarity", "children"),
        Output("fragment-40-similarity-cosine-root", "children"),
        Output("fragment-40-similarity-pearson", "children"),
        Output("fragment-40-similarity-scholle", "children")],
        [Input('name-dropdown', 'value'),
        Input('name-dropdown-Mol', 'value'),
        Input('opt-dropdown-spectrum', 'value')]
    )
    def fragm_40_only_fragment(name, name_mol, id2):
        if name == None or id2==None or name_mol==None:
            fig = go.Figure()
            fig.update_layout(
                margin=dict(t=0, b=0, r=40, l=40),
                height=300,
                xaxis_showticklabels=True,
                xaxis_title='m/z'
            )
            return fig, fig, "", "", "", "" 
        name = [i['blob_name'] for i in blobs if name in i['blob_name']][0]
        mzml_file = FILE_PATH_BASE + name
        run = pymzml.run.Reader(mzml_file)

        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z'
        )
        # get mode in name
        mode = 'Data independant' if ('allion' in name) else 'Data dependant'

        # get id of spec and its energy
        try:
            spec_id = re.search(r'spectrum (.*?) ', id2).group(1)
            spec_ev = re.search(r'of (.*?) eV', id2).group(1)        
        except:
            return fig, fig, "", "", "", ""

        # this small script gets the following spec after the scan
        flag_out = -1
        for spec in run:
            if flag_out == 0 and spec['collision energy'] == 40.0:
                break
            if spec.ID == int(spec_id):
                flag_out = 2 if (mode == 'Data independant') else 3     # in independant mode there is no 10ev collision energy
            flag_out += -1

        p = pymzml.plot.Factory()
        p.new_plot()
        p.add(spec.peaks("centroided"), color=(0, 0, 0), style="sticks", name="peaks")
        X = list(p.plots[0][0].x)
        Y = list(p.plots[0][0].y)
        fig1 = go.Figure()
        fig1.add_trace(
            go.Scatter(
                x=X,
                y=Y,
                mode="lines",
                name=f"Spectrum with energy collision of {get_colision_energy(spec)} eV",
                line=dict(color="rgb(150, 200, 250)"),
                showlegend=False,
            )
        )
        mass = df[df['Name']==name_mol].values[0][2]
        fig1.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z',
            yaxis_title='Relative intensity',
            xaxis = dict(range=[0,mass+2])
        )

        if name.split('/')[-2]=='NEG':
            ionisation = 'Negative'
        if name.split('/')[-2]=='POS':
            ionisation = 'Positive'

        collision_energy = 40

        df1 = df[(df['Name']==name_mol) & (df['Ion Polarity']==ionisation) & (df['Collision Energy']==collision_energy)]
        fragment_masses = df1.T.values[-2]
        try:
            m_max = max(fragment_masses)
        except:
            return fig, fig, "", "", "", ""

        tup1 = spec.peaks('centroided').tolist()
        tup2 = spec.peaks('centroided').tolist()

        for i in tup1:
            for m in fragment_masses:
                min_m = m-0.002
                max_m = m+0.002
                if i[0] > min_m and i[0] < max_m:
                    i[1]=0

        I1 = np.array([I[1] for I in tup1])
        I2 = np.array([I[1] for I in tup2])
        I = I2 - I1
        I_max = np.max(I)
        m_z = np.array([I[0] for I in tup1])


        X = [i for i in m_z.tolist() if i<m_max+1]
        Y = (I * 100 / I_max).tolist()[:len(X)]
        x=[]
        y=[]
        for i in range(len(X)):
            x.append(X[i])
            x.append(X[i])
            x.append(X[i])
            x.append(None)
            y.append(0.0)
            y.append(Y[i])
            y.append(0.0)
            y.append(None)
        fig2 = go.Figure()
        fig2.add_trace(
            go.Scatter(
                x=x,
                y=y,
                mode="lines",
                name="Fragmentation 10 eV",
                line=dict(color="rgb(150, 200, 250)"),
                showlegend=False,
            )
        )
        fig2.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z',
            yaxis_title='Relative intensity',
            xaxis = dict(range=[0,mass+2])
        )


        base_X = df1.T.values[-2].tolist()
        base_Y = df1.T.values[-1].tolist()

        X_, Y_ = [], []
        for i,j in enumerate(base_X):
            L=[]
            for k,l in enumerate(X):
                if abs(j-l)<=0.003:
                    L.append([abs(j-l),Y[k]])
            X_.append(j)
            # If we dont find any pic in experimental profile we put 0 as intensity for this mass
            if len(L)==0:
                Y_.append(0)
            # if we find more than one pic we take the closest pic in m/z
            else:
                min_couple = 1
                min_index = 0
                for index_couple, couple in enumerate(L):
                    if couple[0]<min_couple:
                        min_couple = couple[0]
                        min_index = index_couple
                Y_.append(L[min_index][1])

        base_Y_root = np.power(np.array(base_Y),.5).tolist()
        Y_root = np.power(np.array(Y_),.5).tolist()
        base_Y_scholle = np.array(base_X)*np.array(base_Y)
        Y_scholle = np.array(base_X)*np.array(Y_)

        cosine_sim = 1 - spatial.distance.cosine(base_Y, Y_)
        cosine_sim_root = 1 - spatial.distance.cosine(base_Y_root, Y_root)
        pearson_sim = 1 - spatial.distance.correlation(base_Y, Y_)
        scholle_sim = 1 - spatial.distance.cosine(base_Y_scholle, Y_scholle)

        return fig1, fig2, str(cosine_sim), str(cosine_sim_root), str(pearson_sim), str(scholle_sim)


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