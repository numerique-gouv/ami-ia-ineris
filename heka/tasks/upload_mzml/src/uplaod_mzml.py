# handling mzml files
import pymzml
# calculating isotopic profiles
from brainpy import isotopic_variants
# to ind peaks from chromato
from scipy.signal import find_peaks
# to calculate smilarity scores
from scipy import spatial
# known useful libraries
import os
import re
import pandas as pd
import numpy as np
import time
from datetime import datetime
# import matplotlib.pyplot as plt
import timeit
# google storgae api
# from google.cloud import storage
# from google.oauth2.service_account import Credentials
# handling postgres database
import psycopg2
import pandas.io.sql as sqlio
from sqlalchemy import create_engine
from io import StringIO
# import all sql queries and functions pre defined in queries.py
from queries import *
# read sdf files
# from rdkit.Chem import PandasTools
# cosine similarity
from scipy.spatial.distance import cosine
from functools import reduce
#import pre trained slearn model
import joblib
#managing uplaod to GCS
from google.cloud import storage
from google.oauth2.service_account import Credentials
import io
import base64
import sys
import os
import json



cfg = json.loads(os.environ["PROVIDER_CREDENTIALS"])
PATHSDFFile = "C:\\Users\\alahssini\\Downloads\\Water PCDL_export_080520.sdf"

FILE_PATH_BASE = "/heka/storage/"
BLOB_PATH_BASE = "Data1/Donnees_MzmL/Etude_demonstration/Eau/"
# FILE_PATH_BASE = "C:\\Users\\alahssini\\Desktop\\mzml\\"
# FILE_PATH_BASE = "/home/kaggle_sir/mzml/Data1/Donnees_MzmL/Etude_demonstration/Eau/"
# FILE_PATH_BASE = "/mydata1/Data1/Donnees_MzmL/Etude_demonstration/Eau/"
# MZML_FILES = ["POS\\"+i for i in os.listdir(FILE_PATH_BASE+"POS")]+["NEG\\"+i for i in os.listdir(FILE_PATH_BASE+"NEG")]
# MZML_FILES = ["POS\\"+i for i in os.listdir(FILE_PATH_BASE+BLOB_PATH_BASE+"POS") if 'EmNAT' in i]+["NEG\\"+i for i in os.listdir(FILE_PATH_BASE+BLOB_PATH_BASE+"NEG") if 'EmNAT' in i]
# MZML_FILES = MZML_FILES[16:17]


def read_and_clean_ineris_bdd():
    # loading ineris bdd
    df = pd.read_csv('C:\\Users\\alahssini\\Desktop\\INERIS\\Besoin1\\Data\\PCDL_contenu_INERIS.csv')
    #Clean the dataframe
    def clean(x):
        if not pd.isna(x):
            s=x.replace(',','.')
            s=float(s)
            return(s)

    COLUMNS_TO_CLEAN = ['Mass', 'Retention Time', 'm/z', 'Intensity']
    for i in COLUMNS_TO_CLEAN:
        df[i]=df[i].apply(clean)



    df = df.drop(columns=['Unnamed: 12'])
    df['Source'] = "INERIS"
    df["Upload Date"] = "2020-01-01"



    # loading PCDL bdd
    df = pd.read_csv('C:\\Users\\alahssini\\Desktop\\INERIS\\Besoin1\\Data\\PCDL_contenu_INERIS.csv')
    #Clean the dataframe
    def clean(x):
        if not pd.isna(x):
            s=x.replace(',','.')
            s=float(s)
            return(s)

    COLUMNS_TO_CLEAN = ['Mass', 'Retention Time', 'm/z', 'Intensity']
    for i in COLUMNS_TO_CLEAN:
        df[i]=df[i].apply(clean)



    df = df.drop(columns=['Unnamed: 12'])
    df.loc[df['Species'] == '(M-H)-', 'Precursor m/z'] = df['Mass']-1.00728
    df.loc[df['Species'] == '(M+H)+', 'Precursor m/z'] = df['Mass']+1.00728
    df.loc[df['Species'] == '(M+Na)+', 'Precursor m/z'] = df['Mass']+22.98922
    df.loc[df['Species'] == '(M+NH4)+', 'Precursor m/z'] = df['Mass']+18.03382
    df['Source'] = "INERIS"
    df["Upload Date"] = "2020-01-01"

    return(df)


#df = read_and_clean_ineris_bdd()


#MOLECULES = df['Name'].drop_duplicates().values
MOLECULES = ['DEHP']
MOLECULES = ['Celiprolol']



def store_ineris_bdd(df, store=False):
    df = df[df['Precursor m/z'].notna()]

    if store:
        # put df in the database
        engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

        # Prepare data
        output = StringIO()
        df.to_csv(output, sep='\t', header=False, index=False)
        output.seek(0)

        # Insert data
        connection = engine.raw_connection()
        cursor = connection.cursor()
        cursor.copy_from(output, 'molecules_bdd_global', sep="\t", null='')
        connection.commit()
        cursor.close()

    return(df) 





def clean_store_PCDL_sdf(PATHSDFFile=PATHSDFFile, store=False):
    # read sdf ifle into dataframe
    df_PCDL = PandasTools.LoadSDF(PATHSDFFile)
    # create non existing columns to uniformize formats between PCDL bdd and Ineris bdd
    df_PCDL['Retention Time'] = None
    df_PCDL['NumSpectra'] = None
    df_PCDL['CCS Count'] = None

    # Function that will help us unnest MASS SPECTRA PEAKS column
    def clean_string_to_list(s):
        return [c for c in s.split('\n')]

    # drop na values
    df_PCDL = df_PCDL[df_PCDL['MASS SPECTRAL PEAKS'].notna()]
    # get rid of dupllicate values
    duplicates = df_PCDL.groupby(['NAME','COLLISION ENERGY','ION MODE'])['NUM PEAKS'].count().reset_index(name='count').sort_values(['count'], ascending=False)

    for i in duplicates[duplicates['count']>1].values:
        df_PCDL = df_PCDL[(df_PCDL['NAME']!=i[0]) | (df_PCDL['COLLISION ENERGY']!=i[1]) | (df_PCDL['ION MODE']!=i[2])]
    # unnest MASS SPECTRA PEAKS column
    df_PCDL['MASS SPECTRAL PEAKS'] = df_PCDL['MASS SPECTRAL PEAKS'].apply(clean_string_to_list)
    df_PCDL = df_PCDL.explode('MASS SPECTRAL PEAKS').reset_index(drop=True)
    # split the column into two columns : m/z and intensities
    df_PCDL['m/z'], df_PCDL['Intensity'] = df_PCDL['MASS SPECTRAL PEAKS'].str.split(' ', 1).str
    # get rid of not used columns
    df_PCDL = df_PCDL[['NAME', 'FORMULA', 'EXACT MASS', 'Retention Time', 'CAS', 'CHEMSPIDER', 'NumSpectra', 'CCS Count', 'COLLISION ENERGY', 'ION MODE', 'IONIZATION', 'PRECURSOR TYPE', 'm/z', 'Intensity', 'PRECURSOR M/Z']]
    # uniformize columns names and values between PCDL bdd and Ineris bdd
    df_PCDL = df_PCDL.rename(columns={'NAME':'Name', 'FORMULA':'Formula', 'EXACT MASS': 'Mass', 'CHEMSPIDER':'ChemSpider', 'COLLISION ENERGY':'Collision Energy', 'ION MODE':'Ion Polarity', 'IONIZATION':'Ion Mode', 'PRECURSOR TYPE':'Species', 'PRECURSOR M/Z':'Precursor m/z'})
    df_PCDL['Ion Mode'] = df_PCDL['Ion Mode'].map({'Esi': 'ESI'})
    df_PCDL['Ion Polarity'] = df_PCDL['Ion Polarity'].map({'POSITIVE':'Positive', 'NEGATIVE':'Negative'})
    # Add source column
    df_PCDL['Source'] = 'Agilent'
    df_PCDL["Upload Date"] = "2020-01-01"
    to_convert = ['Mass', 'Collision Energy', 'm/z', 'Intensity', 'Precursor m/z']
    for i in to_convert:
        df_PCDL[i] = df_PCDL[i].apply(lambda x : float(x))


    df_PCDL = df_PCDL.drop_duplicates()

    if store:
        # put df in the database
        engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

        # Prepare data
        output = StringIO()
        df_PCDL.to_csv(output, sep='\t', header=False, index=False)
        output.seek(0)

        # Insert data
        connection = engine.raw_connection()
        cursor = connection.cursor()
        cursor.copy_from(output, 'molecules_bdd_global', sep="\t", null='')
        connection.commit()
        cursor.close()

    return(df_PCDL) 

def get_compo(str):
    """
    get dictionnary of chemical formula instead of string
    """
    element_pat = re.compile("([A-Z][a-z]?)(\d*)")
    all_elements = {}
    for (element_name, count) in element_pat.findall(str):
        if count == "":
            count = 1
        else:
            count = int(count)
        all_elements[element_name]=count
    return(all_elements)



def fill_in_molecule_table(store=False):
    """
    fill in molecule table
    """
    sql = f'SELECT * FROM public.molecules_bdd_global;'
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df = sqlio.read_sql_query(sql, connection)
    connection.close()
    # let only columns that we need
    df1 = df[['name', 'cas', 'formula', 'mass', 'retention_time', 'species', 'ion_polarity', 'precursor_mz', 'upload_date', 'source']]
    # get rid of duplicates
    df2 = df1.drop_duplicates()
    # Create id_molecule with unique index of each row
    df2.reset_index(drop=True, inplace=True)
    df2.reset_index(drop=False, inplace=True)
    df_with_index = df2.rename(columns={'index':'id_molecule'})

    if store:
        # put df in the database
        engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

        # Prepare data
        output = StringIO()
        df_with_index.to_csv(output, sep='\t', header=False, index=False)
        output.seek(0)

        # Insert data
        connection = engine.raw_connection()
        cursor = connection.cursor()
        cursor.copy_from(output, 'molecules', sep="\t", null='')
        connection.commit()
        cursor.close()


    return(df_with_index)

def get_all_mzml():
    """
    returns all mzml files names in the db
    """
    sql = f"SELECT mzml_file FROM public.mzml_files;"
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df = sqlio.read_sql_query(sql, connection)
    connection.close()
    return(df.T.values[0])

def get_id_mzml_by_file(mzml_file):
    """
    returns id_mzml using mzml_file
    """
    sql = f"SELECT id_mzml FROM public.mzml_files where mzml_file='{mzml_file}';"
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df = sqlio.read_sql_query(sql, connection)
    connection.close()
    if len(df)==0:
        print('mzml_file name does not exist in db')
        return()
    return(df.values[0][0])



def get_chromato(mzml_file):
    """
    returns two lists of the same shape : X which is a list of time points and Y which is a list of TIC for this time
    mzml_file is the name of mzml file without the FILE_PATH_BASE
    """
    run = pymzml.run.Reader(FILE_PATH_BASE+mzml_file)
    pf = pymzml.plot.Factory()
    pf.new_plot()
    pf.add(run["TIC"].peaks(), color=(0, 0, 0), style="lines", title='chromato')
    X = list(pf.plots[0][0].x)
    Y = list(pf.plots[0][0].y)
    return(X,Y)


def mzml_flies_carac(mzml_file, id_mzml):
    """
    returns all caracteristics to fill mzml_files table
    mzml_file is the name of mzml file without the FILE_PATH_BASE
    """
    run = pymzml.run.Reader(FILE_PATH_BASE+mzml_file)
    # just to get n which is the number of spectrums
    for n,spec in enumerate(run):
        continue
    if mzml_file[:3]=="POS":
        ionisation = "POS"
    if mzml_file[:3]=="NEG":
        ionisation = "NEG"
    if "-allion-" in mzml_file:
        mode_acq = "Data independant"
        sampling_site = mzml_file.split('-')[mzml_file.split('-').index('allion')-1]
    if "-MSMS-" in mzml_file:
        mode_acq = "Data dependant"
        sampling_site = mzml_file.split('-')[mzml_file.split('-').index('MSMS')-1]
    upload_date = datetime.now().strftime('%Y-%m-%d') 
    sampling_date = 'Null'
    return([id_mzml, mzml_file, ionisation, mode_acq, n, upload_date, sampling_site, sampling_date])


def get_mzml_carac_from_db(mzml_file):
    """
    get mzml caracteristics from db
    """
    sql = f"SELECT * FROM public.mzml_files where mzml_file='{mzml_file}';"
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df = sqlio.read_sql_query(sql, connection)
    connection.close()
    if len(df)==0:
        print('mzml_file name does not exist in db')
        return()
    return(df)


def get_list_molecule_ids_by_ionization(ionization_mode):
    """
    get list of molecule ids by ionaization
    ionization_mode should be equal to : Positive/Negative
    """
    sql = f"SELECT id_molecule FROM public.molecules where ion_polarity='{ionization_mode}';"
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df = sqlio.read_sql_query(sql, connection)
    connection.close()
    return(df.T.values[0])


def get_molecule_crac_by_id(id_molecule):
    """
    get molecule caract by id
    """
    sql = f"SELECT * FROM public.molecules where id_molecule='{id_molecule}';"
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df = sqlio.read_sql_query(sql, connection)
    connection.close()
    if len(df)==0:
        print('id_molecule does not exist in db')
        return()
    return(df)


def search_mass_in_mzml(mzml_file, id_molecule):
    """
    returns two lists : X which is a list of minutes and Y TIC for mass that we are looking for
    """
    df = get_molecule_crac_by_id(id_molecule)
    m_to_look_for = df['precursor_mz'].values[0]
    rt = df['retention_time'].values[0]
    run = pymzml.run.Reader(FILE_PATH_BASE + mzml_file)
    L=[]
    for n, spec in enumerate(run):
        if spec['collision energy'] == None:
            spec_tronc = spec.reduce(mz_range=(m_to_look_for-0.002,m_to_look_for+0.002)).tolist()
            I = sum([i[1] for i in spec_tronc])
            L.append([spec.scan_time_in_minutes(), I])
    X = [i[0] for i in L]
    Y = [i[1] for i in L]
    if rt:
        Z = [max([i[1] for i in L]) if ((i[0]<=rt+0.2) & (i[0]>=rt-0.2)) else 0 for i in L]
        return(X,Y,Z)
    Z = [0 for i in L]
    return(X,Y,Z)



def search_mass_in_mzml_from_db(id_mzml, id_molecule, id_analysis):
    sql = f"SELECT time, tic FROM public.search_mass_mzml where id_mzml={id_mzml} and id_molecule={id_molecule} and id_analysis={id_analysis};"
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df = sqlio.read_sql_query(sql, connection)
    connection.close()
    if len(df)==0:
        print('id_molecule or id_mzml does not exist in db')
        return()
    return(df)

def get_extracted_peaks(mzml_file, acq_mode, ionisation, id_molecule, X=[], Y=[], maching=[], pos_threshold=10000, neg_threshold=1000):
    """
    return all characteristics to fill table extracted_peaks
    X and Y are the result of searching a molecule on a chromatorgram
    """
    if len(X)==0 and len(Y)==0:
        X,Y,Z = search_mass_in_mzml(mzml_file, id_molecule)

    if len(maching)==0:
        # store maching between spec_id and retention time and energy collision of each spec
        run = pymzml.run.Reader(FILE_PATH_BASE + mzml_file)
        maching = []
        for n, spec in enumerate(run):
            maching.append([n,spec.ID, spec['collision energy'], round(spec.scan_time_in_minutes(),2), spec['selected ion m/z']])


    # get mass of the molecule we are looking for
    df = get_molecule_crac_by_id(id_molecule)
    precursor_mz = df['precursor_mz'].values[0]
    real_mz = df['mass'].values[0]
    # extract peaks, the prominence is choosen to be 10000 for positive ionization and 1000 for negative ionization
    prominence = pos_threshold if ionisation=='POS' else neg_threshold
    peaks, _ = find_peaks(Y, prominence=prominence, distance=20)
    X_peaks = np.array(X)[peaks].tolist()
    Y_peaks = np.array(Y)[peaks].tolist()
    # open mzml_file
    run = pymzml.run.Reader(FILE_PATH_BASE + mzml_file)
    # create list to store results 
    ms_exp = []
    ids_spec_scan = []
    ids_spec_frag_10 = []
    ids_spec_frag_20 = []
    ids_spec_frag_40 = []

    if acq_mode == 'Data independant':
        for x_peak in X_peaks:
            id_spec_scan = min([i for i in maching if i[2]==None], key=lambda x:abs(x[3]-x_peak))[1] 
            ids_spec_scan.append(id_spec_scan)
            ids_spec_frag_20.append(min([i for i in maching if i[2]==20.0], key=lambda x:abs(x[3]-x_peak))[1])
            ids_spec_frag_40.append(min([i for i in maching if i[2]==40.0], key=lambda x:abs(x[3]-x_peak))[1])
            ids_spec_frag_10.append(None)
            # In all what follows we try to find the mass detected by our LCMS within we are on positive or nagative ionisation
            spec = run[id_spec_scan]
            spec_tronc = spec.reduce(mz_range=(precursor_mz-0.002,precursor_mz+0.002)).tolist()
            spec_tronc = [i[0]-precursor_mz+real_mz for i in spec_tronc if i[1]>0]
            ms_exp.append(min(spec_tronc, key=lambda x:abs(x-real_mz)))

    elif acq_mode == 'Data dependant':
        for x_peak in X_peaks:
            id_spec_scan = min([i for i in maching if i[2]==None], key=lambda x:abs(x[3]-x_peak))[1] 
            ids_spec_scan.append(id_spec_scan)
            try:
                # to handle case when the molecule is not picked for 10eV
                ids_spec_frag_10.append(min([i for i in maching if i[2]==10.0 and abs(i[4]-precursor_mz)<0.01], key=lambda x:abs(x[4]-precursor_mz))[1])
            except:
                ids_spec_frag_10.append(None)
            try:
                # to handle case when the molecule is not picked for 20eV
                ids_spec_frag_20.append(min([i for i in maching if i[2]==20.0 and abs(i[4]-precursor_mz)<0.01], key=lambda x:abs(x[4]-precursor_mz))[1])
            except:
                ids_spec_frag_20.append(None)
            try:
                # to handle case when the molecule is not picked for 40eV
                ids_spec_frag_40.append(min([i for i in maching if i[2]==40.0 and abs(i[4]-precursor_mz)<0.01], key=lambda x:abs(x[4]-precursor_mz))[1])
            except:
                ids_spec_frag_40.append(None)
                
            # In all what follows we try to find the mass detected by our LCMS within we are on positive or nagative ionisation
            spec = run[id_spec_scan]
            spec_tronc = spec.reduce(mz_range=(precursor_mz-0.002,precursor_mz+0.002)).tolist()
            spec_tronc = [i[0]-precursor_mz+real_mz for i in spec_tronc if i[1]>0]
            ms_exp.append(min(spec_tronc, key=lambda x:abs(x-real_mz)))


    return(ms_exp, X_peaks, Y_peaks, ids_spec_scan, ids_spec_frag_10, ids_spec_frag_20, ids_spec_frag_40)

def get_list_molecule_found_in_mzml(id_mzml, id_analysis):
    sql = f"SELECT id_molecule, retention_time_exp, id_spec_scan FROM public.extracted_peaks WHERE id_mzml = {id_mzml} AND id_analysis = {id_analysis} AND retention_time_exp != 0;"
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df = sqlio.read_sql_query(sql, connection)
    connection.close()
    if len(df)==0:
        print('No molecule found in the mzML')
        return()
    return(df)

def get_isotopic_profile(mzml_file, id_molecule, retention_time_exp, id_spec_scan):
    """
    returns list of m/z exp and theoric and their tics exp and theoric for isotopic profile
    """
    df = get_molecule_crac_by_id(id_molecule)
    precursor_mz = df['precursor_mz'].values[0]
    real_mz = df['mass'].values[0]
    Formula = df['formula'].values[0] 
    # The D molecule is not recognized by brainpy
    if 'D' in Formula:
        return([],[],[],[])
    mol = get_compo(Formula)

    # use brainpy to generate theoric isotopic profile
    theoretical_isotopic_cluster = isotopic_variants(mol, npeaks=10, charge=0)
    # to add the shift between theoric isottopic profil and the experimental one sothat they will be comparated
    X1 = [peak.mz+precursor_mz-real_mz for peak in theoretical_isotopic_cluster]
    Y1 = [peak.intensity for peak in theoretical_isotopic_cluster]
    # normalize to have profile with percentage
    Y1 = [100*y/max(Y1) for y in Y1]

    # we get rid of all pics that are under 0.1%
    indexes = []
    for indx,perc in enumerate(Y1):
        if perc < 0.1:
            indexes.append(indx)
    for index in sorted(indexes, reverse=True):
        del X1[index]
        del Y1[index]


    # get experimental isotopic profile
    run = pymzml.run.Reader(FILE_PATH_BASE + mzml_file)
    spec = run[id_spec_scan]
    spec_tronc = spec.reduce(mz_range=(precursor_mz-2,precursor_mz+10))
    X = [i[0] for i in spec_tronc for j in X1 if abs(i[0]-j)<=0.003]
    Y = [i[1] for i in spec_tronc for j in X1 if abs(i[0]-j)<=0.003]
    try:
        Y = 100 * np.array(Y)/max(Y)
    except:
        pass

    # peak alignement
    X_, Y_ = [], []
    for i,j in enumerate(X1):
        L=[]
        for k,l in enumerate(X):
            if abs(j-l)<=0.003:
                L.append([abs(j-l),Y[k]])
        # If we dont find any pic in experimental profile we put 0 as intensity for this mass
        if len(L)==0:
            Y_.append(0)
            X_.append(j)
        # if we find more than one pic we take the closest pic in m/z
        else:
            min_couple = 1
            min_index = 0
            for index_couple, couple in enumerate(L):
                if couple[0]<min_couple:
                    min_couple = couple[0]
                    min_index = index_couple
            Y_.append(L[min_index][1])
            X_.append(abs(j-L[min_index][0]))

    return(X1, Y1, X_, Y_)

def get_list_molecule_found_in_mzml_by_collision_energy(id_mzml, id_analysis, collision_energy):
    sql = f"SELECT id_molecule, retention_time_exp, {collision_energy} as collision_energy, id_spec_frag_{collision_energy} AS id_spec_frag FROM public.extracted_peaks WHERE id_mzml = {id_mzml} AND retention_time_exp != 0 AND id_analysis = {id_analysis} AND id_spec_frag_{collision_energy} is not null;"
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df = sqlio.read_sql_query(sql, connection)
    connection.close()
    # if len(df)==0:
    #     print(f"""No spec fragmentation for {collision_energy} in the mzML""")
    #     return()
    return(df)

def get_theoric_bdd_fragments(id_molecule, collision_energy):
    """
    Returns by id_molecule all fragments
    """
    # get molecule caracteristique
    df = get_molecule_crac_by_id(id_molecule)
    name = df['molecule_name'].values[0]
    ion_polarity = df['ion_polarity'].values[0]
    species = df['species'].values[0]
    source = df['source'].values[0]
    sql = f"""SELECT mz, intensity FROM public.molecules_bdd_global WHERE name = '{name}' AND collision_energy = {collision_energy}
              AND ion_polarity = '{ion_polarity}' AND species = '{species}' AND source = '{source}';"""
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df = sqlio.read_sql_query(sql, connection)
    connection.close()
    if len(df)==0:
        print('No fragmentation found for the id_molecule')
        return()
    return(df)
    

def get_fragments(mzml_file, id_molecule, collision_energy, id_spec):
    """
    returns list of m/z exp and theoric and their tics exp and theoric for fragment profiles
    """
    if id_spec==None:
        return([], [], [], [])


    df = get_theoric_bdd_fragments(id_molecule, collision_energy)

    if len(df)==0:
        return([], [], [], [])

    fragment_masses = df['mz'].values
    relative_intensities = df['intensity'].values


    # get experimental spectrum
    run = pymzml.run.Reader(FILE_PATH_BASE + mzml_file)
    spec = run[id_spec]
    spec_tronc = spec.reduce(mz_range=(0,1000))
    X = [i[0] for i in spec_tronc for j in fragment_masses if abs(i[0]-j)<=0.003]
    Y = [i[1] for i in spec_tronc for j in fragment_masses if abs(i[0]-j)<=0.003]
    try:
        Y = 100 * np.array(Y)/max(Y)
    except:
        pass

    # peak alignement
    X_, Y_ = [], []
    for i,j in enumerate(fragment_masses):
        L=[]
        for k,l in enumerate(X):
            if abs(j-l)<=0.003:
                L.append([abs(j-l),Y[k]])
        # If we dont find any pic in experimental profile we put 0 as intensity for this mass
        if len(L)==0:
            Y_.append(0)
            X_.append(j)
        # if we find more than one pic we take the closest pic in m/z
        else:
            min_couple = 1
            min_index = 0
            for index_couple, couple in enumerate(L):
                if couple[0]<min_couple:
                    min_couple = couple[0]
                    min_index = index_couple
            Y_.append(L[min_index][1])
            X_.append(abs(j-L[min_index][0]))

    return(fragment_masses.tolist(), relative_intensities.tolist(), X_, Y_)



def get_df_full_query(query):
    conn_string = "host={} \
        port=5432 dbname={} user={} \
        password={}".format(
        HOSTNAME,
        USER,
        USER,
        PASSWORD,
    )
    conn = psycopg2.connect(conn_string)
    df = sqlio.read_sql_query(query, conn)
    conn.close()
    return df


def similarities_isotopic(x):
    """
    get isotopic features
    """
    d = {}
    d['cosine_similarity_isotopic'] = 1 - cosine(x['tic_exp'], x['tic_theoric'])
    d['root_similarity_isotopic'] = 1 - cosine(pow(x['tic_exp'],0.5), pow(x['tic_theoric'],0.5))
    #if Y_ contains only one pic of 100% we compare all the vectors
    if [i for i in x.tic_theoric.values if i>0.1]==[100]:
        d['cosine_similarity_isotopic_mod'] = 1 - cosine(x['tic_exp'], x['tic_theoric'])
    #if Y_ is a nulle vector return 0
    elif [i for i in x.tic_theoric.values if i!=0]==[]:
        d['cosine_similarity_isotopic_mod'] = 0
    # elif we dont take into account the first pic of 100%
    else:
        d['cosine_similarity_isotopic_mod'] = 1 - cosine(x['tic_exp'][1:], x['tic_theoric'][1:])
    d['num_isotopic_the_peaks'] = len([i for i in x.tic_exp.values if i>0])
    d['num_isotopic_exp_peaks'] = len([i for i in x.tic_theoric.values if i>0])
    return pd.Series(d, index=['cosine_similarity_isotopic', 'root_similarity_isotopic', 'num_isotopic_the_peaks', 'num_isotopic_exp_peaks', 'cosine_similarity_isotopic_mod'])

def similarities(x):
    """
    get fragment features
    """
    d = {}
    d['cosine_similarity'] = 1 - cosine(x['tic_exp'], x['tic_theoric'])
    d['root_similarity'] = 1 - cosine(pow(x['tic_exp'],0.5), pow(x['tic_theoric'],0.5))
    d['scholle_similarity'] = 1 - cosine(x['tic_exp']*x['mz_exp'], x['tic_theoric']*x['mz_theoric'])
    d['num_fragmentation_the_peaks'] = len([i for i in x.tic_exp.values if i>0])
    d['num_fragmentation_exp_peaks'] = len([i for i in x.tic_theoric.values if i>0])
    return pd.Series(d, index=['cosine_similarity', 'root_similarity', 'scholle_similarity', 'num_fragmentation_the_peaks', 'num_fragmentation_exp_peaks'])


def get_molecules_in_mzml(id_mzml, id_analysis):
    """
    get all molecules found in mzml
    """
    query_molceules_id_in_mzml = f"select id_molecule from public.fragment where id_mzml={id_mzml} AND id_analysis={id_analysis} group by 1 order by 1"
    df_molceules_id_in_mzml = get_df_full_query(query_molceules_id_in_mzml)
    molecule_ids = df_molceules_id_in_mzml.id_molecule.values
    return(molecule_ids)

def get_dataset_for_mzml(id_mzml, id_analysis):
    """
    build dataset f of found molecules with similarity scores in one mzml
    """
    molecule_ids = get_molecules_in_mzml(id_mzml, id_analysis)
    # print(len(molecule_ids))
    df = pd.DataFrame()
    for id, molecule_id in enumerate(molecule_ids):
        print(f"{len(molecule_ids)-id}/{len(molecule_ids)} molecule to finish for id_mzml : {id_mzml}")
        print(f"id_molecule : {molecule_id}")

        query_extracted_peaks = f"select id_mzml, id_molecule, retention_time_exp, tic, mass_exp from public.extracted_peaks where id_mzml={id_mzml} and id_molecule={molecule_id} AND id_analysis={id_analysis} order by 2"
        df_extracted_peaks = get_df_full_query(query_extracted_peaks)
        # print(df_extracted_peaks)

        # fragments
        query_fragment = f"select * from public.fragment where id_mzml={id_mzml} and id_molecule={molecule_id} AND id_analysis={id_analysis} order by 2"
        df_fragment = get_df_full_query(query_fragment)

        group_by_column = ['id_mzml','id_molecule', 'retention_time_exp', 'collision_energy']

        df_grouped = df_fragment.groupby(group_by_column).apply(similarities).reset_index()
        # print(df_grouped)

        d_fragment = df_grouped.set_index(['retention_time_exp']).pivot(
            # index='retention_time_exp',
            columns='collision_energy')[['cosine_similarity','root_similarity','scholle_similarity', 'num_fragmentation_the_peaks', 'num_fragmentation_exp_peaks']].reset_index()
        d_fragment.columns = ['retention_time_exp']+[f"{i[0]}_{int(i[1])}" for i in d_fragment.columns[1:]]

        # print(d_fragment)

        # istopic profile
        query_isotopic = f"select * from public.isotopic_profile where id_mzml={id_mzml} and id_molecule={molecule_id} AND id_analysis={id_analysis} order by 2"
        df_isotopic = get_df_full_query(query_isotopic)

        group_by_column_isotopic = ['retention_time_exp']

        df_grouped_isotopic = df_isotopic.groupby(group_by_column_isotopic).apply(similarities_isotopic).reset_index()
        # print(df_grouped_isotopic)

        dfs=[df_extracted_peaks, d_fragment, df_grouped_isotopic]
        df_final = reduce(lambda left,right: pd.merge(left,right,on='retention_time_exp'), dfs)

        # mass + RT molecule
        query_molecule_rt = f"select retention_time, mass from public.molecules where id_molecule={molecule_id}"
        df_molecule_rt = get_df_full_query(query_molecule_rt)

        df_final['retention_time'] = df_molecule_rt.retention_time.values[0]
        df_final['mass'] = df_molecule_rt.mass.values[0]
        # print(df_final)
        df = df.append(df_final)
    return(df.reset_index(drop=True))


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



def uplaod_file(mzml_name):
    """Lists all the blobs in the bucket"""
    storage_client = _storage_client()
    bucket_name = _bucket_name()
    bucket = storage_client.get_bucket(bucket_name)
    ionisation= 'POS' if 'pos' in mzml_name[-15:] else 'NEG'
    blob=bucket.blob(f'Data1/Donnees_MzmL/Etude_demonstration/Eau/{ionisation}/{mzml_name}')
    # decoded = base64.b64decode(mzml_content)
    # output = io.StringIO(decoded.decode('utf-8'))
    blob.upload_from_filename(FILE_PATH_BASE+BLOB_PATH_BASE+f'{ionisation}/{mzml_name}',content_type='application/octet-stream')
    # file = open(FILE_PATH_BASE+BLOB_PATH_BASE+f'{ionisation}/{mzml_name}', 'w')
    # file.write(output.getvalue())
    # file.close()


def download_file(mzml_name):
    """Lists all the blobs in the bucket"""
    storage_client = _storage_client()
    bucket_name = _bucket_name()
    bucket = storage_client.get_bucket(bucket_name)
    ionisation= 'NEG' if 'neg' in mzml_name[-15:] else 'POS'
    blob=bucket.blob(f'Data1/Donnees_MzmL/Etude_demonstration/Eau/{ionisation}/{mzml_name}')
    # decoded = base64.b64decode(mzml_content)
    # output = io.StringIO(decoded.decode('utf-8'))
    blob.download_to_filename(f'./{mzml_name}')
    # file = open(FILE_PATH_BASE+BLOB_PATH_BASE+f'{ionisation}/{mzml_name}', 'w')
    # file.write(output.getvalue())
    # file.close()


if __name__ == "__main__" :
    # create tables if not exists, feel free to choose only to create some tables with commenting in file queries.py queries that
    # you don't want to run
    # for query in QUERIES:
    #     run_query(query)


    # # Table mzml_files
    # for i, mzml_file in enumerate(MZML_FILES):
    #     print([i]+mzml_flies_carac(mzml_file))

    # # Table molecules
    # df1 = df[['Name', 'CAS', 'Formula', 'Mass', 'Retention Time', 'Upload Date', 'Source']].drop_duplicates().reset_index(drop=True)
    # df1['Id Molecule'] = df1.index
    # df1 = df1[['Id Molecule', 'Name', 'CAS', 'Formula', 'Mass', 'Retention Time', 'Upload Date', 'Source']]
    # print(df1)



    # # # # Table search_mass_mzml
    # MZML_FILES = get_all_mzml()
    # for i, mzml_file in enumerate(MZML_FILES[60:70]):
    #     start = timeit.default_timer()
    #     df_mzml = get_mzml_carac_from_db(mzml_file)
    #     id_mzml = df_mzml['id_mzml'].values[0]
    #     ionization_mode = df_mzml['ionisation'].values[0]
    #     ionization_mode = 'Positive' if ionization_mode=='POS' else 'Negative'
    #     molecule_ids = get_list_molecule_ids_by_ionization(ionization_mode)
    #     for id_molecule in molecule_ids:
    #         X,Y,Z = search_mass_in_mzml(mzml_file, id_molecule)
    #         df_search = pd.DataFrame({'id_mzml': [id_mzml for i in X], 'id_molecule':[id_molecule for i in X], 'id_analysis':[1 for i in X], 'time':X, 'tic':Y, 'tic_rt':Z})
    #         print(df_search)
    #         # put df in the database
    #         engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

    #         # Prepare data
    #         output = StringIO()
    #         df_search.to_csv(output, sep='\t', header=False, index=False)
    #         output.seek(0)

    #         # Insert data
    #         connection = engine.raw_connection()
    #         cursor = connection.cursor()
    #         cursor.copy_from(output, 'search_mass_mzml', sep="\t", null='')
    #         connection.commit()
    #         cursor.close()
    #     stop = timeit.default_timer()
    #     print('Time: ', stop - start)



    # # # # Table extracted_peaks !!!!!!!
    # MZML_FILES = get_all_mzml()
    # for i, mzml_file in enumerate(MZML_FILES[58:60]):
    #     print(mzml_file)
    #     start = timeit.default_timer()
    #     df_mzml = get_mzml_carac_from_db(mzml_file)
    #     id_mzml = df_mzml['id_mzml'].values[0]
    #     ionization_mode = df_mzml['ionisation'].values[0]
    #     ionization_mode_long = 'Positive' if ionization_mode=='POS' else 'Negative'
    #     acquisition_mode = df_mzml['acquisition_mode'].values[0]
    #     molecule_ids = get_list_molecule_ids_by_ionization(ionization_mode_long)
    #     # store maching between spec_id and retention time and energy collision of each spec
    #     run = pymzml.run.Reader(FILE_PATH_BASE + mzml_file)
    #     maching = []
    #     for n, spec in enumerate(run):
    #         maching.append([n,spec.ID, spec['collision energy'], round(spec.scan_time_in_minutes(),2), spec['selected ion m/z']])
    #     for id_molecule in molecule_ids:
    #         df_search_mass_in_mzml = search_mass_in_mzml_from_db(id_mzml, id_molecule)
    #         ms_exp, X_peaks, Y_peaks, ids_spec_scan, ids_spec_frag_10, ids_spec_frag_20, ids_spec_frag_40 = get_extracted_peaks(mzml_file, acquisition_mode, ionization_mode, id_molecule, X=df_search_mass_in_mzml['time'].values, Y=df_search_mass_in_mzml['tic'].values, maching=maching)
    #         if len(ms_exp)==0 :
    #             df_search = pd.DataFrame({'id_mzml': [id_mzml], 'id_molecule':[id_molecule], 'id_analysis':[1], 'mass_exp':[None], 'retention_time_exp':[0], 'tic':[None], 'id_spec_scan':[None], 'id_spec_frag_10':[None], 'id_spec_frag_20':[None], 'id_spec_frag_40':[None]})
    #             print(df_search)
    #         else :
    #             df_search = pd.DataFrame({'id_mzml': [id_mzml for i in ms_exp], 'id_molecule':[id_molecule for i in ms_exp], 'id_analysis':[1 for i in ms_exp], 'mass_exp':ms_exp, 'retention_time_exp':X_peaks, 'tic':Y_peaks, 'id_spec_scan':ids_spec_scan, 'id_spec_frag_10':ids_spec_frag_10, 'id_spec_frag_20':ids_spec_frag_20, 'id_spec_frag_40':ids_spec_frag_40})
    #             print(df_search)
    #         # put df in the database
    #         engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

    #         # Prepare data
    #         output = StringIO()
    #         df_search.to_csv(output, sep='\t', header=False, index=False)
    #         output.seek(0)

    #         # Insert data
    #         connection = engine.raw_connection()
    #         cursor = connection.cursor()
    #         cursor.copy_from(output, 'extracted_peaks', sep="\t", null='')
    #         connection.commit()
    #         cursor.close()
    #     stop = timeit.default_timer()
    #     print('Time: ', stop - start)




    # # # # Table isotopic_profile
    # MZML_FILES = get_all_mzml()
    # for i, mzml_file in enumerate(MZML_FILES[1:30]):
    #     print(mzml_file)
    #     start = timeit.default_timer()
    #     df_mzml = get_mzml_carac_from_db(mzml_file)
    #     id_mzml = df_mzml['id_mzml'].values[0]
    #     ionization_mode = df_mzml['ionisation'].values[0]
    #     ionization_mode = 'Positive' if ionization_mode=='POS' else 'Negative'
    #     acquisition_mode = df_mzml['acquisition_mode'].values[0]
    #     df_molecule_ids = get_list_molecule_found_in_mzml(id_mzml)
    #     if len(df_molecule_ids) == 0:
    #         continue
    #     molecule_ids = df_molecule_ids.values

    #     for id_molecule, retention_time_exp, id_spec_scan in molecule_ids:
    #         X1, Y1, X_, Y_ = get_isotopic_profile(mzml_file.replace('\\','/'), int(id_molecule), retention_time_exp, int(id_spec_scan))
    #         if len(X1)==0:
    #             continue

    #         df_isotopic_profile = pd.DataFrame({'id_mzml': [id_mzml for i in X1], 'id_molecule':[int(id_molecule) for i in X1], 'id_analysis':[1 for i in X1], 'retention_time_exp':[retention_time_exp for i in X1], 'id_spec_scan':[int(id_spec_scan) for i in X1], 'mz_exp':X1, 'tic_exp':Y1, 'mz_theoric':X_, 'tic_theoric':Y_})
    #         print(df_isotopic_profile)
    #         # put df in the database
    #         engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

    #         # Prepare data
    #         output = StringIO()
    #         df_isotopic_profile.to_csv(output, sep='\t', header=False, index=False)
    #         output.seek(0)

    #         # Insert data
    #         connection = engine.raw_connection()
    #         cursor = connection.cursor()
    #         cursor.copy_from(output, 'isotopic_profile', sep="\t", null='')
    #         connection.commit()
    #         cursor.close()
    #     stop = timeit.default_timer()
    #     print('Time: ', stop - start)


    
    # # # Table fragments !!!!!!!!!!!!!
    # MZML_FILES = get_all_mzml()
    # for i, mzml_file in enumerate(MZML_FILES[58:60]):
    #     print(mzml_file)
    #     start = timeit.default_timer()
    #     df_mzml = get_mzml_carac_from_db(mzml_file)
    #     id_mzml = df_mzml['id_mzml'].values[0]
    #     ionization_mode = df_mzml['ionisation'].values[0]
    #     ionization_mode = 'Positive' if ionization_mode=='POS' else 'Negative'
    #     acquisition_mode = df_mzml['acquisition_mode'].values[0]
    #     df_molecule_10_ids = get_list_molecule_found_in_mzml_by_collision_energy(id_mzml, 10)
    #     df_molecule_20_ids = get_list_molecule_found_in_mzml_by_collision_energy(id_mzml, 20)
    #     df_molecule_40_ids = get_list_molecule_found_in_mzml_by_collision_energy(id_mzml, 40)
    #     df_molecule_ids = df_molecule_10_ids.append(df_molecule_20_ids).append(df_molecule_40_ids).reset_index(drop=True)
    #     if len(df_molecule_ids) == 0:
    #         continue
    #     molecule_ids = df_molecule_ids.values
    #     # molecule_ids=[[184, 10.638033333333, 20, 639033]]

    #     for id_molecule, retention_time_exp, collision_energy, id_spec in molecule_ids:
    #         X1, Y1, X_, Y_ = get_fragments(mzml_file, int(id_molecule), collision_energy, int(id_spec))
    #         if len(X1)==0:
    #             continue

    #         df_isotopic_profile = pd.DataFrame({'id_mzml': [id_mzml for i in X1], 'id_molecule':[int(id_molecule) for i in X1], 'id_analysis':[1 for i in X1], 'retention_time_exp':[retention_time_exp for i in X1], 'collision_energy':[int(collision_energy) for i in X1], 'id_spec':[int(id_spec) for i in X1], 'mz_exp':X1, 'tic_exp':Y1, 'mz_theoric':X_, 'tic_theoric':Y_})
    #         print(df_isotopic_profile)
    #         # put df in the database
    #         engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

    #         # Prepare data
    #         output = StringIO()
    #         df_isotopic_profile.to_csv(output, sep='\t', header=False, index=False)
    #         output.seek(0)

    #         # Insert data
    #         connection = engine.raw_connection()
    #         cursor = connection.cursor()
    #         cursor.copy_from(output, 'fragment', sep="\t", null='')
    #         connection.commit()
    #         cursor.close()
    #     stop = timeit.default_timer()
    #     print('Time: ', stop - start)



    # df_molecule_10_ids = get_list_molecule_found_in_mzml_by_collision_energy(4, 10)
    # df_molecule_20_ids = get_list_molecule_found_in_mzml_by_collision_energy(4, 20)
    # df_molecule_40_ids = get_list_molecule_found_in_mzml_by_collision_energy(4, 40)
    # print(df_molecule_10_ids)
    # print('-'*50)
    # print(df_molecule_20_ids)
    # print('-'*50)
    # print(df_molecule_40_ids)
    # print('-'*50)
    # print(df_molecule_10_ids.append(df_molecule_20_ids).append(df_molecule_40_ids).reset_index(drop=True))

    # print(get_list_molecule_found_in_mzml_by_collision_energy(3, 10))





    # # Table extracted_peaks
    # for i, mzml_file in enumerate(MZML_FILES):
    #     for molecule in MOLECULES:
    #         start = timeit.default_timer()
    #         print(get_extracted_peaks(mzml_file, molecule))
    #         stop = timeit.default_timer()
    #         print('Time: ', stop - start)

    # # Table isotopic_profile
    # for i, mzml_file in enumerate(MZML_FILES):
    #     for molecule in MOLECULES:
    #         start = timeit.default_timer()
    #         print(get_isotopic_profile(mzml_file, molecule, 14.5786, 874724))
    #         stop = timeit.default_timer()
    #         print('Time: ', stop - start)

    # Table fragments
    # for i, mzml_file in enumerate(MZML_FILES):
    #     for molecule in MOLECULES:
    #         # start = timeit.default_timer()
    #         # print(get_fragments(mzml_file, molecule, 20.0, 720591))
    #         # stop = timeit.default_timer()
    #         # print('Time: ', stop - start)
    #         start = timeit.default_timer()
    #         X,Y,Z,A = get_fragments(mzml_file, molecule, 40.0, 720848)
    #         print(Y)
    #         print("-"*100)
    #         print(A)
    #         stop = timeit.default_timer()
    #         print('Time: ', stop - start)


    # df = clean_store_PCDL_sdf(PATHSDFFile=PATHSDFFile, store=True)
    # print(df)

    # store_ineris_bdd(store=True)

    # df = fill_in_molecule_table(store=True)
    # print(df)

    # print(get_id_mzml_by_file('POS\\06-09_18-6-014-N-luech-MSMS-pos-1.mzML'))


####################################################################################
    # get args
    # for line in sys.stdin:
    #     print(line)
    #     break
        
    MZML_FILES=sys.argv[1:]
    print(MZML_FILES)
    for i in MZML_FILES:
        download_file(i)
        print(f"dowloaded : {i}")
        run = pymzml.run.Reader(f'./{i}')
        print('run done')


       
    # # table mzml_files
    # for id_mzml,mzml_file in enumerate(MZML_FILES):
    #     sql = f'SELECT max(id_mzml) FROM public.mzml_files;'
    #     connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    #     df = sqlio.read_sql_query(sql, connection)
    #     connection.close()
    #     id_mzml = df.values[0,0]+1
    #     caracs = mzml_flies_carac(mzml_file, id_mzml)
    #     print(caracs)
    #     add_2_mzml_files(caracs)


    # # Table mzml_chromato
    # for mzml_file in MZML_FILES:
    #     X,Y = get_chromato(mzml_file)
    #     id_mzml = get_id_mzml_by_file(mzml_file)
    #     df_chromato = pd.DataFrame({'id_mzml':[id_mzml for i in range(len(X))], 'time':X, 'tic':Y})
    #     print(df_chromato)
    #     # put df in the database
    #     engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

    #     # Prepare data
    #     output = StringIO()
    #     df_chromato.to_csv(output, sep='\t', header=False, index=False)
    #     output.seek(0)

    #     # Insert data
    #     connection = engine.raw_connection()
    #     cursor = connection.cursor()
    #     cursor.copy_from(output, 'mzml_chromato', sep="\t", null='')
    #     connection.commit()
    #     cursor.close()


    # pos_threshold = 10000
    # neg_threshold = 1000
    # sql = f'SELECT max(id_analysis) FROM public.analysis;'
    # connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    # df = sqlio.read_sql_query(sql, connection)
    # connection.close()
    # id_analysis = df.values[0,0]+1  #dont forget ot add 1 when decommenting the next line add_2_analysis
    # add_2_analysis([id_analysis, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), pos_threshold, neg_threshold, 0.003, 0.2, 'Null', 'Null'])
    

    # start = timeit.default_timer()
    # # # Table search_mass_mzml
    # for i, mzml_file in enumerate(MZML_FILES):
    #     df_mzml = get_mzml_carac_from_db(mzml_file)
    #     id_mzml = df_mzml['id_mzml'].values[0]
    #     ionization_mode = df_mzml['ionisation'].values[0]
    #     ionization_mode = 'Positive' if ionization_mode=='POS' else 'Negative'
    #     molecule_ids = get_list_molecule_ids_by_ionization(ionization_mode)
    #     for id_molecule in molecule_ids:
    #         X,Y,Z = search_mass_in_mzml(mzml_file, id_molecule)
    #         df_search = pd.DataFrame({'id_mzml': [id_mzml for i in X], 'id_molecule':[id_molecule for i in X], 'id_analysis':[id_analysis for i in X], 'time':X, 'tic':Y, 'tic_rt':Z})
    #         print(df_search)
    #         # put df in the database
    #         engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

    #         # Prepare data
    #         output = StringIO()
    #         df_search.to_csv(output, sep='\t', header=False, index=False)
    #         output.seek(0)

    #         # Insert data
    #         connection = engine.raw_connection()
    #         cursor = connection.cursor()
    #         cursor.copy_from(output, 'search_mass_mzml', sep="\t", null='')
    #         connection.commit()
    #         cursor.close()


    # # # # Table extracted_peaks
    # for i, mzml_file in enumerate(MZML_FILES):
    #     print(mzml_file)
    #     # start = timeit.default_timer()
    #     df_mzml = get_mzml_carac_from_db(mzml_file)
    #     id_mzml = df_mzml['id_mzml'].values[0]
    #     ionization_mode = df_mzml['ionisation'].values[0]
    #     ionization_mode_long = 'Positive' if ionization_mode=='POS' else 'Negative'
    #     acquisition_mode = df_mzml['acquisition_mode'].values[0]
    #     molecule_ids = get_list_molecule_ids_by_ionization(ionization_mode_long)
    #     # store maching between spec_id and retention time and energy collision of each spec
    #     run = pymzml.run.Reader(FILE_PATH_BASE + mzml_file)
    #     maching = []
    #     for n, spec in enumerate(run):
    #         maching.append([n,spec.ID, spec['collision energy'], round(spec.scan_time_in_minutes(),2), spec['selected ion m/z']])
    #     for id_molecule in molecule_ids:
    #         df_search_mass_in_mzml = search_mass_in_mzml_from_db(id_mzml, id_molecule, id_analysis)
    #         ms_exp, X_peaks, Y_peaks, ids_spec_scan, ids_spec_frag_10, ids_spec_frag_20, ids_spec_frag_40 = get_extracted_peaks(mzml_file, acquisition_mode, ionization_mode, id_molecule, X=df_search_mass_in_mzml['time'].values, Y=df_search_mass_in_mzml['tic'].values, maching=maching)
    #         if len(ms_exp)==0 :
    #             df_search = pd.DataFrame({'id_mzml': [id_mzml], 'id_molecule':[id_molecule], 'id_analysis':[id_analysis], 'mass_exp':[None], 'retention_time_exp':[0], 'tic':[None], 'id_spec_scan':[None], 'id_spec_frag_10':[None], 'id_spec_frag_20':[None], 'id_spec_frag_40':[None]})
    #             print(df_search)
    #         else :
    #             df_search = pd.DataFrame({'id_mzml': [id_mzml for i in ms_exp], 'id_molecule':[id_molecule for i in ms_exp], 'id_analysis':[id_analysis for i in ms_exp], 'mass_exp':ms_exp, 'retention_time_exp':X_peaks, 'tic':Y_peaks, 'id_spec_scan':ids_spec_scan, 'id_spec_frag_10':ids_spec_frag_10, 'id_spec_frag_20':ids_spec_frag_20, 'id_spec_frag_40':ids_spec_frag_40})
    #             print(df_search)
    #         # put df in the database
    #         engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

    #         # Prepare data
    #         output = StringIO()
    #         df_search.to_csv(output, sep='\t', header=False, index=False)
    #         output.seek(0)

    #         # Insert data
    #         connection = engine.raw_connection()
    #         cursor = connection.cursor()
    #         cursor.copy_from(output, 'extracted_peaks', sep="\t", null='')
    #         connection.commit()
    #         cursor.close()
    #     # stop = timeit.default_timer()
    #     # print('Time: ', stop - start)

    # # # # Table isotopic_profile
    # for i, mzml_file in enumerate(MZML_FILES):
    #     print(mzml_file)
    #     # start = timeit.default_timer()
    #     df_mzml = get_mzml_carac_from_db(mzml_file)
    #     id_mzml = df_mzml['id_mzml'].values[0]
    #     ionization_mode = df_mzml['ionisation'].values[0]
    #     ionization_mode = 'Positive' if ionization_mode=='POS' else 'Negative'
    #     acquisition_mode = df_mzml['acquisition_mode'].values[0]
    #     df_molecule_ids = get_list_molecule_found_in_mzml(id_mzml, id_analysis)
    #     if len(df_molecule_ids) == 0:
    #         continue
    #     molecule_ids = df_molecule_ids.values

    #     for id_molecule, retention_time_exp, id_spec_scan in molecule_ids:
    #         X1, Y1, X_, Y_ = get_isotopic_profile(mzml_file, int(id_molecule), retention_time_exp, int(id_spec_scan))
    #         if len(X1)==0:
    #             continue

    #         df_isotopic_profile = pd.DataFrame({'id_mzml': [id_mzml for i in X1], 'id_molecule':[int(id_molecule) for i in X1], 'id_analysis':[id_analysis for i in X1], 'retention_time_exp':[retention_time_exp for i in X1], 'id_spec_scan':[int(id_spec_scan) for i in X1], 'mz_exp':X1, 'tic_exp':Y1, 'mz_theoric':X_, 'tic_theoric':Y_})
    #         print(df_isotopic_profile)
    #         # put df in the database
    #         engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

    #         # Prepare data
    #         output = StringIO()
    #         df_isotopic_profile.to_csv(output, sep='\t', header=False, index=False)
    #         output.seek(0)

    #         # Insert data
    #         connection = engine.raw_connection()
    #         cursor = connection.cursor()
    #         cursor.copy_from(output, 'isotopic_profile', sep="\t", null='')
    #         connection.commit()
    #         cursor.close()
    #     # stop = timeit.default_timer()
    #     # print('Time: ', stop - start)


    # # # Table fragments
    # for i, mzml_file in enumerate(MZML_FILES):
    #     print(mzml_file)
    #     # start = timeit.default_timer()
    #     df_mzml = get_mzml_carac_from_db(mzml_file)
    #     id_mzml = df_mzml['id_mzml'].values[0]
    #     ionization_mode = df_mzml['ionisation'].values[0]
    #     ionization_mode = 'Positive' if ionization_mode=='POS' else 'Negative'
    #     acquisition_mode = df_mzml['acquisition_mode'].values[0]
    #     df_molecule_10_ids = get_list_molecule_found_in_mzml_by_collision_energy(id_mzml, id_analysis, 10)
    #     df_molecule_20_ids = get_list_molecule_found_in_mzml_by_collision_energy(id_mzml, id_analysis, 20)
    #     df_molecule_40_ids = get_list_molecule_found_in_mzml_by_collision_energy(id_mzml, id_analysis, 40)
    #     df_molecule_ids = df_molecule_10_ids.append(df_molecule_20_ids).append(df_molecule_40_ids).reset_index(drop=True)
    #     if len(df_molecule_ids) == 0:
    #         continue
    #     molecule_ids = df_molecule_ids.values
    #     # molecule_ids=[[184, 10.638033333333, 20, 639033]]

    #     for id_molecule, retention_time_exp, collision_energy, id_spec in molecule_ids:
    #         X1, Y1, X_, Y_ = get_fragments(mzml_file, int(id_molecule), collision_energy, int(id_spec))
    #         if len(X1)==0:
    #             continue

    #         df_isotopic_profile = pd.DataFrame({'id_mzml': [id_mzml for i in X1], 'id_molecule':[int(id_molecule) for i in X1], 'id_analysis':[id_analysis for i in X1], 'retention_time_exp':[retention_time_exp for i in X1], 'collision_energy':[int(collision_energy) for i in X1], 'id_spec':[int(id_spec) for i in X1], 'mz_exp':X1, 'tic_exp':Y1, 'mz_theoric':X_, 'tic_theoric':Y_})
    #         print(df_isotopic_profile)
    #         # put df in the database
    #         engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

    #         # Prepare data
    #         output = StringIO()
    #         df_isotopic_profile.to_csv(output, sep='\t', header=False, index=False)
    #         output.seek(0)

    #         # Insert data
    #         connection = engine.raw_connection()
    #         cursor = connection.cursor()
    #         cursor.copy_from(output, 'fragment', sep="\t", null='')
    #         connection.commit()
    #         cursor.close()
    #     # stop = timeit.default_timer()
    #     # print('Time: ', stop - start)


    # for i, mzml_file in enumerate(MZML_FILES):
    #     df_mzml = get_mzml_carac_from_db(mzml_file)
    #     id_mzml = df_mzml['id_mzml'].values[0]
    #     acquisition_mode = df_mzml['acquisition_mode'].values[0]

    #     d=get_dataset_for_mzml(id_mzml, id_analysis)

    #     L = ['id_mzml','id_molecule', 'id_analysis', 'retention_time_exp','tic','mass_exp','cosine_similarity_10','cosine_similarity_20','cosine_similarity_40','root_similarity_10','root_similarity_20','root_similarity_40','scholle_similarity_10','scholle_similarity_20','scholle_similarity_40','num_fragmentation_the_peaks_10','num_fragmentation_the_peaks_20','num_fragmentation_the_peaks_40','num_fragmentation_exp_peaks_10','num_fragmentation_exp_peaks_20','num_fragmentation_exp_peaks_40','cosine_similarity_isotopic','root_similarity_isotopic','num_isotopic_the_peaks','num_isotopic_exp_peaks','cosine_similarity_isotopic_mod','retention_time','mass']
        
    #     if acquisition_mode=='Data independant':
    #         L1 = ['cosine_similarity_10','root_similarity_10','scholle_similarity_10','num_fragmentation_the_peaks_10','num_fragmentation_exp_peaks_10']
    #         for i in L1:
    #             d[i]=None
        
    #     d['id_analysis']=id_analysis
    #     d = d[L]
    #     print(d)
    #     # put df in the database
    #     engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

    #     # Prepare data
    #     output = StringIO()
    #     d.to_csv(output, sep='\t', header=False, index=False)
    #     output.seek(0)

    #     # Insert data
    #     connection = engine.raw_connection()
    #     cursor = connection.cursor()
    #     cursor.copy_from(output, 'score_similarities', sep="\t", null='')
    #     connection.commit()
    #     cursor.close()

    #     RFC_non28_3 = joblib.load('RFC_non28_3.pkl')
    #     RFC_non28_3_ineris = joblib.load('RFC_non28_3_ineris.pkl')

    #     X1_ret = ['rt_diff_abs', 'cosine_similarity_20', 'scholle_similarity_20', 'cosine_similarity_40','scholle_similarity_40', 'cosine_similarity_isotopic_mod', 'found_peaks_isotopic']
    #     X1 = ['cosine_similarity_20', 'scholle_similarity_20', 'cosine_similarity_40', 'scholle_similarity_40', 'cosine_similarity_isotopic_mod', 'found_peaks_isotopic']
    #     d['rt_diff']=d['retention_time_exp']-d['retention_time']
    #     d['rt_diff_abs'] = d['rt_diff'].apply(lambda x : abs(x))
    #     d['found_peaks_isotopic'] = d['num_isotopic_exp_peaks'].apply(lambda x : 0 if x==1 else 1)
    #     d = d[['id_mzml', 'id_molecule', 'id_analysis', 'retention_time_exp']+X1_ret]
    #     d[X1] = d[X1].fillna(0)
    #     d['prob'] = d[X1_ret].apply(lambda x: RFC_non28_3_ineris.predict_proba([x])[0,1] if(np.all(pd.notnull(x[0]))) else RFC_non28_3.predict_proba([x[1:]])[0,1], axis = 1)
    #     d['class'] = d[X1_ret].apply(lambda x: RFC_non28_3_ineris.predict([x])[0] if(np.all(pd.notnull(x[0]))) else RFC_non28_3.predict([x[1:]])[0], axis = 1)
    #     print(d)

    #     # put df in the database
    #     engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

    #     # Prepare data
    #     output = StringIO()
    #     d.to_csv(output, sep='\t', header=False, index=False)
    #     output.seek(0)

    #     # Insert data
    #     connection = engine.raw_connection()
    #     cursor = connection.cursor()
    #     cursor.copy_from(output, 'scores', sep="\t", null='')
    #     connection.commit()
    #     cursor.close()
    
    # stop = timeit.default_timer()
    # print('Time: ', stop - start)
