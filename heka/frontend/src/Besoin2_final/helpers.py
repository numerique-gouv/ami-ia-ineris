import yaml
import json
import os
import psycopg2
import pandas as pd
import pandas.io.sql as sqlio
import numpy as np
from sqlalchemy import create_engine

conversion = {
        "distance" : "Distance_à_la_source_km",
        "matrice" : "Matrice",
        "projet" : "Nom_du_projet",
        "mesure" : "Type_de_point_de_mesure"}

columns_ind = ["id", "Nom_du_projet", "Sous-catégorie", "Matrice", "Distance_à_la_source_km", "Type_de_point_de_mesure", "Unités"]
substances = ['2378-TCDD', '12378-PeCDD', '123478-HxCDD', '123678-HxCDD',
    '123789-HxCDD', '1234678-HpCDD', 'OCDD', '2378-TCDF', '12378-PeCDF',
    '23478-PeCDF', '123478-HxCDF', '123678-HxCDF', '234678-HxCDF',
    '123789-HxCDF', '1234678-HpCDF', '1234789-HpCDF', 'OCDF']
total_homologue = ['Total_TCDD', 'Total_PeCDD', 'Total_HxCDD', 'Total_HpCDD', 'OCDD', 
    'Total_TCDF', 'Total_PeCDF', 'Total_HxCDF', 'Total_HpCDF', 'OCDF']
substances_A = [sub + '_A' for sub in substances]
substances_C = [sub + '_C' for sub in substances]

list_color = ["#000000", "#d62a00", "#ff4400", "#ff8a00", "#ffcd00", "#ffeb00"]
list_color_police = ["white", "white", "white", "white", "black", "black",]
list_value = [15 * i / (len(list_color) - 1) for i in range(len(list_color))] + [100]

def get_df(query):
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

def get_categories():
    query = "SELECT DISTINCT "
    for key in conversion:
        if(key != "mesure"):
            query += "\"" + conversion[key] + "\" AS " + str(key) + ", "
        else:
            query += "\"" + conversion[key] + "\" AS " + str(key) + " "
    query += "FROM public.data_ineris"
    return get_df(query)

df_categories_final = get_categories()

def get_all_data():
    query = """SELECT * FROM public.data_ineris WHERE \"OCDD_A\" IS NOT NULL"""
    result = get_df(query)
    result["id"] = result.index
    result = result[columns_ind + substances + substances_A + substances_C]
    return result

df = get_all_data()
df[substances_A] = round(df[substances_A] * 100, 2)
df[substances_C] = round(df[substances_C] * 100, 2)

def set_all_data(df, db):
    conf = yaml.load(os.environ["PROJECT_CONFIG"], Loader=yaml.SafeLoader)
    db_connection_url = "postgresql://{}:{}@{}:{}/{}".format(
        conf["project-database"]["user"],
        conf["project-database"]["password"],
        conf["project-database"]["hostname"],
        conf["project-database"]["port"],
        conf["project-database"]["name"],
    )

    engine = create_engine(db_connection_url)
    df.to_sql(db, engine, if_exists='replace', index=False)
    engine.dispose()