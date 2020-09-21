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
# google storgae api
from google.cloud import storage
from google.oauth2.service_account import Credentials
# handling postgres database
import psycopg2
import pandas.io.sql as sqlio
# import all sql queries and functions pre defined in queries.py
from queries import *

import matplotlib.pyplot as plt
import timeit



FILE_PATH_BASE = "C:\\Users\\alahssini\\Desktop\\mzml\\"
MZML_FILES = ["POS\\"+i for i in os.listdir(FILE_PATH_BASE+"POS")]+["NEG\\"+i for i in os.listdir(FILE_PATH_BASE+"NEG")]
# for now i will work only with one mzml which is MZML_FILES[1]
MZML_FILES = MZML_FILES[1:2]
MZML_FILES = ["POS\\27-08_18-6-014-Q-escaut-allion-pos-1.mzML"]

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


MOLECULES = df['Name'].drop_duplicates().values
MOLECULES = ['DEHP']
MOLECULES = ['Celiprolol']



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


def mzml_flies_carac(mzml_file):
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
    if "MSMS" in mzml_file:
        mode_acq = "Data dependant"
        sampling_site = mzml_file.split('-')[mzml_file.split('-').index('MSMS')-1]
    if "allion" in mzml_file:
        mode_acq = "Data independant"
        sampling_site = mzml_file.split('-')[mzml_file.split('-').index('allion')-1]
    upload_date = "2020-01-01" 
    sampling_date = None
    return([mzml_file, ionisation, mode_acq, n, upload_date, sampling_site, sampling_date])



def search_mass_in_mzml(mzml_file, molecule):
    """
    returns two lists : X which is a list of minutes and Y TIC for mass that we are looking for
    """
    df1 = df[df['Name']==molecule]
    m = df1.values[0][2]
    rt = df1.values[0][3]
    run = pymzml.run.Reader(FILE_PATH_BASE + mzml_file)
    L=[]
    for n, spec in enumerate(run):
        if spec['collision energy'] == None:
            if spec['negative scan']=='':
                spec_tronc = spec.reduce(mz_range=(m-0.002-1.00728,m+0.002-1.00728)).tolist()
            elif spec['positive scan']=='':
                spec_tronc = spec.reduce(mz_range=(m-0.002+1.00728,m+0.002+1.00728)).tolist()
            I = sum([i[1] for i in spec_tronc])
            L.append([spec.scan_time_in_minutes(), I])
    X = [i[0] for i in L]
    Y = [i[1] for i in L]
    Z = [max([i[1] for i in L]) if ((i[0]<=rt+0.2) & (i[0]>=rt-0.2)) else 0 for i in L]
    return(X,Y,Z)


def get_extracted_peaks(mzml_file, molecule, X=None, Y=None):
    """
    return all characteristics to fill table extracted_peaks
    X and Y are the result of searching a molecule on a chromatorgram
    """
    if X==None and Y==None:
        X,Y,Z = search_mass_in_mzml(mzml_file, molecule)

    # get mass of the molecule we are looking for
    df1 = df[df['Name']==molecule]
    m = df1.values[0][2]
    # extract peaks
    peaks, _ = find_peaks(Y, prominence=10000, distance=20)
    X_peaks = np.array(X)[peaks].tolist()
    Y_peaks = np.array(Y)[peaks].tolist()
    # store maching between spec_id and retention time and energy collision of each spec
    run = pymzml.run.Reader(FILE_PATH_BASE + mzml_file)
    maching = []
    for n, spec in enumerate(run):
        maching.append([n,spec.ID, spec['collision energy'], round(spec.scan_time_in_minutes(),2)])
    # create listto store reuslts 
    ms_exp = []
    ids_spec_scan = []
    ids_spec_frag_10 = []
    ids_spec_frag_20 = []
    ids_spec_frag_40 = []

    for x_peak in X_peaks:
        id_spec_scan = min([i for i in maching if i[2]==None], key=lambda x:abs(x[3]-x_peak))[1] 
        ids_spec_scan.append(id_spec_scan)
        ids_spec_frag_20.append(min([i for i in maching if i[2]==20.0], key=lambda x:abs(x[3]-x_peak))[1])
        ids_spec_frag_40.append(min([i for i in maching if i[2]==40.0], key=lambda x:abs(x[3]-x_peak))[1])
        try:
            # to handle case of allion when we do not have collision energy of 10
            ids_spec_frag_10.append(min([i for i in maching if i[2]==10.0], key=lambda x:abs(x[3]-x_peak))[1])
        except:
            ids_spec_frag_10.append(None)
        # In all what follows we try to find the mass detected by our LCMS within we are on positive or nagative ionisation
        spec = run[id_spec_scan]
        if spec['negative scan']=='':
            spec_tronc = spec.reduce(mz_range=(m-0.002-1.00728,m+0.002-1.00728)).tolist()
            spec_tronc = [i[0]+1.00728 for i in spec_tronc if i[1]>0]
            ms_exp.append(min(spec_tronc, key=lambda x:abs(x-m)))
        elif spec['positive scan']=='':
            spec_tronc = spec.reduce(mz_range=(m-0.002+1.00728,m+0.002+1.00728)).tolist()
            spec_tronc = [i[0]-1.00728 for i in spec_tronc if i[1]>0]
            ms_exp.append(min(spec_tronc, key=lambda x:abs(x-m)))
    return(ms_exp, X_peaks, Y_peaks, ids_spec_scan, ids_spec_frag_10, ids_spec_frag_20, ids_spec_frag_40)



def get_isotopic_profile(mzml_file, molecule, retention_time_exp, id_spec_scan):
    """
    returns list of m/z exp and theoric and their tics exp and theoric for isotopic profile
    """
    Formula = df[df['Name']==molecule]['Formula'].values[0]
    mol = get_compo(Formula)
    if mzml_file[:3]=='NEG':
        charge = -1
    if mzml_file[:3]=='POS':
        charge = 1

    # use brainpy to generate theoric isotopic profile
    theoretical_isotopic_cluster = isotopic_variants(mol, npeaks=10, charge=charge)
    X1 = [peak.mz for peak in theoretical_isotopic_cluster]
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

    # get mass of the molecule we are looking for
    df1 = df[df['Name']==molecule]
    m = df1.values[0][2]
    # get experimental isotopic profile
    run = pymzml.run.Reader(FILE_PATH_BASE + mzml_file)
    spec = run[id_spec_scan]
    spec_tronc = spec.reduce(mz_range=(m,m+11))
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


def get_fragments(mzml_file, molecule, collision_energy, id_spec):
    """
    returns list of m/z exp and theoric and their tics exp and theoric for fragment profiles
    """
    if id_spec==None:
        return([], [], [], [])

    if mzml_file[:3]=="POS":
        ionisation = "Positive"
    if mzml_file[:3]=="NEG":
        ionisation = "Negative"

    df1 = df[(df['Name']==molecule) & (df['Ion Polarity']==ionisation) & (df['Collision Energy']==collision_energy)]
    fragment_masses = df1.T.values[-4]
    relative_intensities = df1.T.values[-3]
    try:
        m_max = max(fragment_masses)
    except:
        pass

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
                L.append([abs(j-l),relative_intensities[k]])
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






if __name__ == "__main__" :
    # create tables if not exists, feel free to choose only to create some tables with commenting in file queries.py queries that
    # you don't want to run
    # for query in QUERIES:
    #     run_query(query)

    # # Table mzml_chromato
    # for mzml_file in MZML_FILES:
    #     X,Y = get_chromato(mzml_file)

    # # Table mzml_files
    # for i, mzml_file in enumerate(MZML_FILES):
    #     print([i]+mzml_flies_carac(mzml_file))

    # # Table molecules
    # df1 = df[['Name', 'CAS', 'Formula', 'Mass', 'Retention Time', 'Upload Date', 'Source']].drop_duplicates().reset_index(drop=True)
    # df1['Id Molecule'] = df1.index
    # df1 = df1[['Id Molecule', 'Name', 'CAS', 'Formula', 'Mass', 'Retention Time', 'Upload Date', 'Source']]
    # print(df1)

    # # Table search_mass_mzml
    # for i, mzml_file in enumerate(MZML_FILES):
    #     for molecule in MOLECULES:
    #         X,Y,Z = search_mass_in_mzml(mzml_file, molecule)

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
    for i, mzml_file in enumerate(MZML_FILES):
        for molecule in MOLECULES:
            # start = timeit.default_timer()
            # print(get_fragments(mzml_file, molecule, 20.0, 720591))
            # stop = timeit.default_timer()
            # print('Time: ', stop - start)
            start = timeit.default_timer()
            X,Y,Z,A = get_fragments(mzml_file, molecule, 40.0, 720848)
            print(Y)
            print("-"*100)
            print(A)
            stop = timeit.default_timer()
            print('Time: ', stop - start)


