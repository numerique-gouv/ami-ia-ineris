from google.cloud import storage
from google.oauth2.service_account import Credentials
import plotly.graph_objects as go
import pymzml
import re
import yaml
import json
import os
import psycopg2
import pandas as pd
import pandas.io.sql as sqlio
import numpy as np
# to calculate smilarity scores
from scipy import spatial


cfg = json.loads(os.environ["PROVIDER_CREDENTIALS"])
FILE_PATH_BASE = '/heka/storage/'


def get_compo(str):
    element_pat = re.compile("([A-Z][a-z]?)(\d*)")
    all_elements = {}
    for (element_name, count) in element_pat.findall(str):
        if count == "":
            count = 1
        else:
            count = int(count)
        all_elements[element_name]=count
    return(all_elements)



def get_df_full_query(query):
    conf = yaml.load(os.environ["PROJECT_CONFIG"], Loader=yaml.SafeLoader)
    conn_string = "host={} \
        port=5432 dbname={} user={} \
        password={}".format(
        conf["project-database"]["hostname"],
        conf["project-database"]["name"],
        conf["project-database"]["user"],
        conf["project-database"]["password"],
    )
    conn = psycopg2.connect(conn_string)
    df = sqlio.read_sql_query(query, conn)
    conn.close()
    return df



def get_colision_energy(spec):
    if spec['collision energy'] == None:
        return(0)
    return(spec['collision energy'])


def get_mzml_values(path):
    mzml_file = FILE_PATH_BASE + path
    run = pymzml.run.Reader(mzml_file)
    L=[]
    for n, spec in enumerate(run):
        L.append(f"spectrum {spec.ID} at RT {round(spec.scan_time_in_minutes(),2)} min and collision energy of {get_colision_energy(spec)} eV")
    return(L)



def _storage_client():
    """retuns the client creds to be used while accessing bucket"""
    credentials = Credentials.from_service_account_info(
        cfg
    )
    client = storage.Client(
        project=credentials.project_id, credentials=credentials
    )
    return client


def _bucket_name():
    credentials = Credentials.from_service_account_info(
        cfg
    )
    env = credentials.project_id.split("-")[-1]
    prefix = credentials.project_id.split("-")[0]
    project_name = credentials.service_account_email.split("@")[0].replace(
        f"{prefix}-", ""
    )
    return f"{prefix}-{env}-{project_name}-storage"





def list_blobs():
    """Lists all the blobs in the bucket"""
    storage_client = _storage_client()
    bucket_name = _bucket_name()
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs()
    return [
        {
            "blob_name": blob.name,
            "size": blob.size,
            "updated": blob.updated,
            "md5_hash": blob.md5_hash,
        }
        for blob in blobs
    ]



def get_mzml_charc(mzml_file):
    query=f"""SELECT * FROM public.mzml_files WHERE mzml_file = '{mzml_file}';"""
    df = get_df_full_query(query)
    return(df)


def update_chromato_carac_db(mzml_file):
    mzml_file_charc = get_mzml_charc(mzml_file.replace('/','\\'))
    id_mzml = mzml_file_charc.id_mzml.values[0]
    ionisation = mzml_file_charc.ionisation.values[0]
    acquisition_mode = mzml_file_charc.acquisition_mode.values[0]
    spectrum_number = mzml_file_charc.spectrum_number.values[0]
    query=f"""SELECT time, tic FROM public.mzml_chromato WHERE id_mzml = {id_mzml} ORDER BY 1;"""
    df = get_df_full_query(query)
    time = df.time.values
    tic = df.tic.values
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=time,
            y=tic,
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
    return(fig, spectrum_number, acquisition_mode, ionisation)

def get_molecule_charc(molecule_name, source, species):
    query=f"""SELECT * FROM public.molecules WHERE molecule_name = '{molecule_name}' AND source ='{source}' AND species='{species}';"""
    df = get_df_full_query(query)
    return(df)


def get_search_mass_mzml(mzml_file, molecule_name, source, species):
    mzml_file_charc = get_mzml_charc(mzml_file.replace('/','\\'))
    molecul_charc = get_molecule_charc(molecule_name, source, species)
    id_mzml = mzml_file_charc.id_mzml.values[0]
    ionisation = mzml_file_charc.ionisation.values[0]
    id_molecule = molecul_charc.id_molecule.values[0]
    m = molecul_charc.mass.values[0]
    query_search=f"""SELECT time, tic, tic_rt FROM public.search_mass_mzml WHERE id_mzml = {id_mzml} AND id_molecule = {id_molecule} ORDER BY 1;"""
    df_search = get_df_full_query(query_search)
    query_peaks=f"""SELECT retention_time_exp, tic, mass_exp FROM public.extracted_peaks WHERE id_mzml = {id_mzml} AND id_molecule = {id_molecule} AND tic>10000 ORDER BY 1;""" if ionisation=='POS' else f"""SELECT retention_time_exp, tic, mass_exp FROM public.extracted_peaks WHERE id_mzml = {id_mzml} AND id_molecule = {id_molecule} ORDER BY 1;""" 
    df_peaks = get_df_full_query(query_peaks)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_search['time'],
            y=df_search['tic'],
            mode="lines",
            name=f'TIC for mass {m}',
            line=dict(color="rgb(100, 150, 200)"),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_search['time'],
            y=df_search['tic_rt'],
            mode="lines",
            name='Theoretical RT',
            line=dict(color="rgb(150, 200, 250)"),
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=df_peaks['retention_time_exp'],
            y=df_peaks['tic'],
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
    if len(df_peaks) == 0:
        return(fig, [])
    peaks_dict = [{"Minute" : df_peaks.retention_time_exp.values[i], "Peak value" : df_peaks.tic.values[i], "Detected mass" : df_peaks.mass_exp.values[i]} for i,j in enumerate(df_peaks.values)]
    
    return(fig, peaks_dict)


def get_bar_pres_from_list(X,Y):
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
    return(x,y)


def get_fragment_from_db(mzml_file, molecule_name, source, species, retention_time_exp, collision_energy):
    mzml_file_charc = get_mzml_charc(mzml_file.replace('/','\\'))
    molecul_charc = get_molecule_charc(molecule_name, source, species)
    id_mzml = mzml_file_charc.id_mzml.values[0]
    ionisation = mzml_file_charc.ionisation.values[0]
    id_molecule = molecul_charc.id_molecule.values[0]
    m = molecul_charc.mass.values[0]
    query=f"""SELECT mz_exp, tic_exp, mz_theoric, tic_theoric FROM public.fragment WHERE id_mzml = {id_mzml} AND id_molecule = {id_molecule} 
              AND retention_time_exp = {retention_time_exp} AND collision_energy = {collision_energy} ORDER BY 1;"""
    df = get_df_full_query(query)

    if len(df)==0:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z'
        )
        return fig, fig, "", "", "", "" 

    X_exp = df['mz_exp']
    Y_exp = df['tic_exp']
    X_the = df['mz_theoric']
    Y_the = df['tic_theoric']

    x_exp, y_exp = get_bar_pres_from_list(X_exp,Y_exp)
    x_the, y_the = get_bar_pres_from_list(X_the,Y_the)


    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=x_exp,
            y=y_exp,
            mode="lines",
            name=f'Experimental fragmentation',
            line=dict(color="rgb(100, 150, 200)"),
            showlegend=False,
        )
    )
    fig1.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        xaxis_showticklabels=True,
        xaxis_title='m/z',
        yaxis_title='Relative intensity',
        xaxis = dict(range=[0,m+2])
    )

    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=x_the,
            y=y_the,
            mode="lines",
            name=f'Theoric fragmentation',
            line=dict(color="rgb(100, 150, 200)"),
            showlegend=False,
        )
    )
    fig2.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        xaxis_showticklabels=True,
        xaxis_title='m/z',
        yaxis_title='Relative intensity',
        xaxis = dict(range=[0,m+2])
    )

    Y_exp_root = np.power(np.array(Y_exp),.5).tolist()
    Y_the_root = np.power(np.array(Y_the),.5).tolist()
    Y_exp_scholle = np.array(X_exp)*np.array(Y_exp)
    Y_the_scholle = np.array(X_the)*np.array(Y_the)

    cosine_sim = 1 - spatial.distance.cosine(Y_exp, Y_the)
    cosine_sim_root = 1 - spatial.distance.cosine(Y_exp_root, Y_the_root)
    pearson_sim = 1 - spatial.distance.correlation(Y_exp, Y_the)
    scholle_sim = 1 - spatial.distance.cosine(Y_exp_scholle, Y_the_scholle)

    return fig2, fig1, str(cosine_sim), str(cosine_sim_root), str(pearson_sim), str(scholle_sim)



def get_isotopic_profile_from_db(mzml_file, molecule_name, source, species, retention_time_exp):
    mzml_file_charc = get_mzml_charc(mzml_file.replace('/','\\'))
    molecul_charc = get_molecule_charc(molecule_name, source, species)
    id_mzml = mzml_file_charc.id_mzml.values[0]
    id_molecule = molecul_charc.id_molecule.values[0]
    m = molecul_charc.mass.values[0]
    query=f"""SELECT mz_exp, tic_exp, mz_theoric, tic_theoric FROM public.isotopic_profile WHERE id_mzml = {id_mzml} 
              AND id_molecule = {id_molecule} AND retention_time_exp = {retention_time_exp} ORDER BY 1;"""
    df = get_df_full_query(query)

    if len(df)==0:
        fig = go.Figure()
        fig.update_layout(
            margin=dict(t=0, b=0, r=40, l=40),
            height=300,
            xaxis_showticklabels=True,
            xaxis_title='m/z'
        )
        return fig, fig, "", "", "", "" 

    X_exp = df['mz_exp']
    Y_exp = df['tic_exp']
    X_the = df['mz_theoric']
    Y_the = df['tic_theoric']

    x_exp, y_exp = get_bar_pres_from_list(X_exp,Y_exp)
    x_the, y_the = get_bar_pres_from_list(X_the,Y_the)


    fig1 = go.Figure()
    fig1.add_trace(
        go.Scatter(
            x=x_exp,
            y=y_exp,
            mode="lines",
            name=f'Experimental isotopic profile',
            line=dict(color="rgb(100, 150, 200)"),
            showlegend=False,
        )
    )
    fig1.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        xaxis_showticklabels=True,
        xaxis_title='m/z',
        yaxis_title='Relative intensity',
        xaxis = dict(range=[min(X_exp)-1,max(X_exp)+1])
    )

    fig2 = go.Figure()
    fig2.add_trace(
        go.Scatter(
            x=x_the,
            y=y_the,
            mode="lines",
            name=f'Theoric isotopic profile',
            line=dict(color="rgb(100, 150, 200)"),
            showlegend=False,
        )
    )
    fig2.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        xaxis_showticklabels=True,
        xaxis_title='m/z',
        yaxis_title='Relative intensity',
        xaxis = dict(range=[min(X_exp)-1,max(X_exp)+1])
    )

    #if Y_ contains only one pic of 100% we compare all the vectors
    if [i for i in Y_exp if i>0.1]==[100]:
        cosine_sim = 1 - spatial.distance.cosine(Y_the, Y_exp)
    #if Y_ is a nulle vector return 0
    elif [i for i in Y_exp if i!=0]==[]:
        cosine_sim = 0
    # elif we dont take into account the first pic of 100%
    else:
        cosine_sim = 1 - spatial.distance.cosine(Y_the[1:], Y_exp[1:])

    return fig2, fig1, str(cosine_sim)