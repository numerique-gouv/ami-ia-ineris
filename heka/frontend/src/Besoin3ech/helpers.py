from google.cloud import storage
from google.oauth2.service_account import Credentials
import dash_html_components as html
import plotly.graph_objects as go
import dash_table
import pymzml
import re
import yaml
import json
import os
import psycopg2
import pandas as pd
import pandas.io.sql as sqlio
import numpy as np
import requests
# to calculate smilarity scores
from scipy import spatial


conf = yaml.load(os.environ["PROJECT_CONFIG"], Loader=yaml.SafeLoader)



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


def tasks(start, end):
    query=f"""SELECT start_time, status, end_time-start_time AS duration 
              FROM launcher.processes 
              WHERE task_id=3 AND (status=0 OR status=1)
              AND '{start}' <= start_time AND start_time <= '{end}'
              ORDER BY 1 DESC;"""
    df = get_df_full_query(query)
    fig = go.Figure()
    fig.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        xaxis_showticklabels=True,
        xaxis_title='Time',
        yaxis_title='Task'
    )
    if len(df)==0:
        return(fig)
    df['duration']=pd.to_numeric(df['duration'].dt.seconds, downcast='integer')
    df['start_time'] = df.start_time.dt.strftime('%Y-%m-%d %H:%M:%S')
    time0 = df[df['status']==0].start_time.values
    time1 = df[df['status']==1].start_time.values
    tic0 = ['CMB Task' for i in time0]
    tic1 = ['CMB Task' for i in time1]
    custom0 = df[df['status']==0].duration.values
    custom1 = df[df['status']==1].duration.values
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=time0,
            y=tic0,
            customdata=custom0,
            mode="markers",
            marker_symbol='circle',
            name="Succes",
            marker_color="rgb(0, 128, 0)",
            showlegend=False,
        )
    )
    fig.add_trace(
        go.Scatter(
            x=time1,
            y=tic1,
            customdata=custom1,
            mode="markers",
            marker_symbol='triangle-down',
            name="Error",
            marker_color="rgb(255, 0, 0)",
            showlegend=False,
        )
    )
    fig.update_layout(
        margin=dict(t=0, b=0, r=40, l=40),
        height=300,
        xaxis_showticklabels=True,
        xaxis_title='Time',
        yaxis_title='Task',
        xaxis_tickformat="%d %B (%a)\n%H:%M",
    )
    return(fig)

def add_2_blacklist_besoin3(row):
    """
    Insert one record to public.blacklist_besoin3
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO blacklist_besoin3 
    (date, model) 
    VALUES('{row[0]}', '{row[1]}');
    """
    run_query(sql)

def run_query(sql):
    """Run sql query"""
    connection = psycopg2.connect(
        user = conf["project-database"]["user"], 
        password = conf["project-database"]["password"],
        host = conf["project-database"]["hostname"], 
        port = "5432", 
        database = conf["project-database"]["name"])
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    connection.close()

