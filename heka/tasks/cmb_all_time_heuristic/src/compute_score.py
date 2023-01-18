# known useful libraries
import os
from typing import List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import datetime
import yaml
# handling postgres database
import psycopg2
import pandas.io.sql as sqlio
from sqlalchemy import create_engine
from io import StringIO
# regressors
from sklearn.linear_model import Lasso
import scipy.odr
#webdav
import requests
import xml.etree.cElementTree as xml
from collections import namedtuple

profiles_list = [
    'HOA',
    'BBOA',
    'OPOA/OBBOA',
    'BSOA (marine)',
    'BSOA (isoprene)',
    'ASOA (nitro-PAHs)',
    'ASOA (oxy-PAHs)',
    'ASOA (phenolic compounds oxidation)',
    'ASOA (toluene oxidation)',
    'SOA (unknown)']

## GLOBAL VARIABLE
model = "LASSO_10_heu"
id_site = 1
id_analysis = 3

## CREDENTIAL DB
conf = yaml.load(os.environ["PROJECT_CONFIG"], Loader=yaml.SafeLoader)
USER = conf["project-database"]["user"]
PASSWORD = conf["project-database"]["password"]
HOSTNAME = conf["project-database"]["hostname"]
PORT = "5432"
DATABASE = conf["project-database"]["name"]


def run_query(sql):
    """Run sql query"""
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    connection.close()


def get_profiles(profiles=profiles_list):
    """
    Get means and std of profiles from db
    profiles : is a list of profile names.
    """
    df = pd.read_excel('./home/pmf_profiles.xlsx', engine='openpyxl')
    df.drop(columns=['Unnamed: 0'], inplace=True)
    df.rename(columns={'Unnamed: 1': 'amus'}, inplace=True)
    df = df[["amus"] + profiles]
    return df

def global_loop(date, profiles):
    df = get_profiles(profiles)

    contribution = []

    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)

    sql = f"""SELECT * FROM public.data_receptor where date = '{date}' 
        order by mass;"""
    df_receptor_data = sqlio.read_sql_query(sql, connection)
    df_receptor_data = df_receptor_data[df_receptor_data.columns]
    cor = df.merge(df_receptor_data, left_on='amus', right_on='mass').drop(columns=['mass', 'amus'])

    connection.close()

    X_train = cor[profiles].values
    y_train = cor['value'].values.reshape(-1,1)

    alpha = 0.0001
    lasso = Lasso(fit_intercept=False, alpha=alpha, max_iter=5000)     # We train without intercept and we shoose to have only positive values
    lasso.fit(X_train, y_train)                                        #training the algorithm

    data_profile = df[profiles].values
    construct = np.dot(data_profile, lasso.coef_)

    # MAE error
    error_mae = np.sum(np.abs(construct - [a[0] for a in y_train])) / len(y_train)

    # MSE error
    error_mse = np.sum(np.abs(construct**2 - np.array([a[0] for a in y_train])**2)) / len(y_train)

    for n, prof in enumerate(profiles):
        contribution.append(lasso.coef_[n])
    
    return contribution, error_mae, error_mse


def run_lasso_heuristique(date, profiles):
    list_profils = []
    seuil_last = np.inf
    best_result = ()

    for i in range(len(profiles)):
        for profil in profiles:
            selected_profil_approx = None
            if profil not in list_profils:
                result, error_mae, error_mse = global_loop(date, list_profils + [profil])
                if error_mae < seuil_last:
                    seuil_last = error_mae
                    selected_profil_approx = profil
                    best_result = (result, error_mae, error_mse)
            if selected_profil_approx is not None:
                list_profils.append(selected_profil_approx)
        else:
            break
    return list_profils, best_result

def add_2_regressor_results(row):
    """
    Insert one record to public.regressor_results
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO regressor_results 
    (date, id_site, id_analysis, model, profile, contribution, uncertainty) 
    VALUES('{row[0]}' , {row[1]} , {row[2]} , '{row[3]}' , '{row[4]}', {row[5]}, {row[6]});
    """
    run_query(sql)


def add_regressor_error(row):
    """
    Insert one record to public.model_error
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO model_error 
    (date, id_site, id_analysis, model, error_type, mass, error, error_relative) 
    VALUES('{row[0]}' , {row[1]} , {row[2]} , '{row[3]}' , '{row[4]}', {row[5]}, {row[6]}, {row[7]});
    """
    run_query(sql)


def compute_store_regressor(date, id_site, id_analysis, profiles=profiles_list):
    """
    compute lasso and odr result for one year and store them in a table
    """
    result_profils, result = run_lasso_heuristique(date, profiles)
    for indx, profile in enumerate(result_profils): 
        try:
            row_lasso_lissage = [date, id_site, id_analysis, model, profile, result[0][indx], 'Null']
            add_2_regressor_results(row_lasso_lissage)
        except:
            print(f'{model} results for datetime :{date} already in table')
    
    try:
        row_lasso_lissage = [date, id_site, id_analysis, model, 'MAE', 0, result[1], 'Null']
        add_regressor_error(row_lasso_lissage)
    except:
        print(f'{model} error MAE for datetime :{date} already in table')

    try:
        row_lasso_lissage = [date, id_site, id_analysis, model, 'MSE', 0, result[2], 'Null']
        add_regressor_error(row_lasso_lissage)
    except:
        print(f'{model} error MSE for datetime :{date} already in table')


connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)

query_date = f"""
    WITH aux1 AS (
        SELECT DISTINCT date
        FROM public.data_receptor
        ORDER BY date),
    aux2 AS (
        SELECT DISTINCT date
        FROM public.regressor_results
        WHERE model = '{model}'
        ORDER BY date)
    SELECT aux1.date
    FROM aux1 LEFT JOIN aux2 ON aux1.date = aux2.date
    WHERE aux2.date IS NULL"""

df_date = sqlio.read_sql_query(query_date, connection)
connection.close()

for value in df_date.values:
    date = value[0]
    print(date)
    compute_store_regressor(date, id_site, id_analysis, profiles_list)
