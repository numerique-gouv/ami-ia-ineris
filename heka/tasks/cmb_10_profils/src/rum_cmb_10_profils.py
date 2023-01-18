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
model = "LASSO_10_full"
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
    df.rename(columns={'Unnamed: 1': 'mass'}, inplace=True)
    df = df[["mass"] + profiles]
    return df


def run_lasso_lissage(date, profiles):
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)

    value = get_profiles(profiles)
    value = value.rename(columns={"mass" : "amus"})

    ## Collect the receptor data
    sql = f"""SELECT * FROM public.data_receptor where date = '{date}'"""
    df_receptor_data = sqlio.read_sql_query(sql, connection)
    df_receptor_data = df_receptor_data[df_receptor_data.columns]

    cor = value.merge(df_receptor_data, left_on='amus', right_on='mass').drop(columns=['mass', 'amus'])

    # Choose variables
    X_train = cor[profiles].values
    y_train = cor['value'].values.reshape(-1,1)

    # Training Lasso Model
    alpha = 0.0001
    lasso = Lasso(fit_intercept=False, alpha=alpha, positive=True, max_iter=5000)
    lasso.fit(X_train, y_train)
                            
    connection.close()
    return lasso.coef_


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


def compute_store_regressor(date, id_site, id_analysis, profiles=profiles_list):
    """
    compute lasso and odr result for one year and store them in a table
    """
    lasso_lissage = run_lasso_lissage(date, profiles)
    for indx, profile in enumerate(profiles): 
        try:
            row_lasso_lissage = [date, id_site, id_analysis, model, profile, lasso_lissage[indx], 'Null']
            add_2_regressor_results(row_lasso_lissage)
        except:
            print(f'{model} results for datetime :{date} already in table')  

def compute_signal_reconst(date, model, id_site, id_analysis):
    """
    reconstitution of signal for one model and one date
    """
    # get data from db
    sql = f"SELECT * FROM public.regressor_results where date = '{date}' and model = '{model}' and id_site = {id_site} and id_analysis = {id_analysis};"
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df = sqlio.read_sql_query(sql, connection)
    connection.close()
    if len(df)==0:
        return([])
    value = get_profiles()
    df_melt = pd.melt(frame=value, id_vars='mass', value_vars=profiles_list, var_name="profile", value_name="value")
    df_join = df.merge(df_melt,how='left',left_on=['profile'],right_on=['profile'])
    df_join['value'] = df_join['contribution']*df_join['value']
    df_join = df_join.groupby(['date', 'id_site', 'id_analysis', 'model', 'mass']).sum().reset_index()[['date', 'id_site', 'id_analysis', 'model', 'mass', 'value']]
    return(df_join)


def get_error(date, model, id_site, id_analysis, error_type, df_signal_recons=[]):
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    sql = f"SELECT * FROM public.data_receptor where date = '{date}' order by mass;"
    df_receptor_data = sqlio.read_sql_query(sql, connection)    
    connection.close()

    if len(df_signal_recons)==0:
        df_signal_recons = compute_signal_reconst(date, model, id_site, id_analysis)
        if len(df_signal_recons)==0:
            return([])

    df_join = df_receptor_data.merge(df_signal_recons,how='left',left_on=['mass'],right_on=['mass'])
    df_join['error_type'] = error_type

    if error_type == "MAE":
        df_join['error'] = abs(df_join['value_x'] - df_join['value_y'])
        df_join['error_relative'] = abs(df_join['value_x'] - df_join['value_y'])/abs(df_join['value_x'])
        df_join = df_join.replace([np.inf, -np.inf], np.nan)
        df_join = df_join[['date_x', 'id_site_x', 'id_analysis', 'model', 'error_type', 'mass', 'error', 'error_relative']].rename(columns={'date_x': 'date', 'id_site_x': 'id_site'})
        global_error = [date, id_site, id_analysis, model, error_type, 0, df_join['error'].sum()/len(df_join['error']), df_join['error_relative'].sum()/len(df_join['error_relative'])]
        df_join.loc[len(df_join)] = global_error



    if error_type == "MSE":
        df_join['error'] = abs(df_join['value_x']**2 - df_join['value_y']**2)
        df_join['error_relative'] = abs(df_join['value_x']**2 - df_join['value_y']**2)/abs(df_join['value_x']**2)
        df_join = df_join.replace([np.inf, -np.inf], np.nan)
        df_join = df_join[['date_x', 'id_site_x', 'id_analysis', 'model', 'error_type', 'mass', 'error', 'error_relative']].rename(columns={'date_x': 'date', 'id_site_x': 'id_site'})
        global_error = [date, id_site, id_analysis, model, error_type, 0, df_join['error'].sum()/len(df_join['error']), df_join['error_relative'].sum()/len(df_join['error_relative'])]
        df_join.loc[len(df_join)] = global_error


    return(df_join)


def compute_store_errors(date, id_site, id_analysis):
    """
    compute lasso and odr result for one year and store them in a table
    """

    ## SIGNA RECONSTITUTION
    df_signal_recons = compute_signal_reconst(date, model, id_site, id_analysis)
    if len(df_signal_recons)==0:
        print(f"df_signal_recons empty")
        return None

    try:
        # put df in the database
        engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

        # Prepare data
        output = StringIO()
        df_signal_recons.to_csv(output, sep='\t', header=False, index=False)
        output.seek(0)

        # Insert data
        connection = engine.raw_connection()
        cursor = connection.cursor()
        cursor.copy_from(output, 'signal_reconst', sep="\t", null='')
        connection.commit()
        cursor.close()
    except:
        print(f'signal reconstitution for {model} in {date} already in table')


    # for error_type in ['MSE', 'MAE']:
    #     print(error_type)
    #     df_error = get_error(date, model, id_site, id_analysis, error_type, df_signal_recons=df_signal_recons)
    #     if len(df_error)==0:
    #         print(f"df_error empty")
    #         continue
    #     try:
    #         # put df in the database
    #         engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

    #         # Prepare data
    #         output = StringIO()
    #         df_error.to_csv(output, sep='\t', header=False, index=False)
    #         output.seek(0)

    #         # Insert data
    #         connection = engine.raw_connection()
    #         cursor = connection.cursor()
    #         cursor.copy_from(output, 'model_error', sep="\t", null='')
    #         connection.commit()
    #         cursor.close()
    #     except:
    #         print(f'Errors for {model} in {date} with error type {error_type} already in table')



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
    compute_store_regressor(date, id_site, id_analysis, profiles=profiles_list)
    compute_store_errors(date, id_site, id_analysis)
