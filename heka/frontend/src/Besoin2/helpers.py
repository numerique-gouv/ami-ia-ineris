import yaml
import json
import os
import psycopg2
import pandas as pd
import pandas.io.sql as sqlio
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

conversion = {
        "distance" : "Distance_à_la_source_km",
        "matrice" : "Matrice",
        "projet" : "Nom_du_projet",
        "mesure" : "Type_de_point_de_mesure"}
substances = ['2378-TCDD', '12378-PeCDD', '123478-HxCDD', '123678-HxCDD',
    '123789-HxCDD', '1234678-HpCDD', 'OCDD', '2378-TCDF', '12378-PeCDF',
    '23478-PeCDF', '123478-HxCDF', '123678-HxCDF', '234678-HxCDF',
    '123789-HxCDF', '1234678-HpCDF', '1234789-HpCDF', 'OCDF']

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

df_categories = get_categories()

def get_data(list_distance, list_matrice, list_projet, list_mesure):
    query = "SELECT * FROM public.data_ineris WHERE True "
    if(list_distance != None and list_distance != ''):
        query += "AND ("
        for (i, distance) in enumerate(list_distance):
            if (i == 0):
                query += "\"" + str(conversion["distance"]) + "\" = '" + str(distance) + "' "
            else:
                query += "OR \"" + str(conversion["distance"]) + "\" = '" + str(distance) + "' "
        query += ") "
    if(list_matrice != None and list_matrice != ''):
        query += "AND ("
        for (i, matrice) in enumerate(list_matrice):
            if (i == 0):
                query += "\"" + str(conversion["matrice"]) + "\" = '" + str(matrice) + "' "
            else:
                query += "OR \"" + str(conversion["matrice"]) + "\" = '" + str(matrice) + "' "
        query += ") "
    if(list_projet != None and list_projet != ''):
        query += "AND ("
        for (i, projet) in enumerate(list_projet):
            if(i == 0):
                query += "\"" + str(conversion["projet"]) + "\" = '" + str(projet) + "' "
            else:
                query += "OR \"" + str(conversion["projet"]) + "\" = '" + str(projet) + "' "
        query += ") "

    if(list_mesure != None and list_mesure != ''):
        query += "AND ("
        for (i, mesure) in enumerate(list_mesure):
            if(i == 0):
                query += "\"" + str(conversion["mesure"]) + "\" = '" + str(mesure) + "' "
            else:
                query += "OR \"" + str(conversion["mesure"]) + "\" = '" + str(mesure) + "' "
        query += ") "
    query = query.replace("AND ()", "")
    return get_df(query)


def dot_product_table(visu):
    df_similarity = pd.DataFrame(columns=[ "Variable_1", "Variable_2", "score"])
    i = 0
    type_mesure = list(visu.index)
    for mesure_1 in type_mesure:
        for mesure_2 in type_mesure:
            df_similarity.loc[i] = [
                mesure_1,
                mesure_2,
                cosine_similarity(visu[visu.index.isin([mesure_1])], visu[visu.index.isin([mesure_2])])[0][0]]
            i += 1

    return pd.pivot_table(df_similarity, values='score', index="Variable_1", columns="Variable_2", aggfunc=sum)