# known useful libraries
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
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


conf = yaml.load(os.environ["PROJECT_CONFIG"], Loader=yaml.SafeLoader)


USER = conf["project-database"]["user"]
PASSWORD = conf["project-database"]["password"]
HOSTNAME = conf["project-database"]["hostname"]
PORT = "5432"
DATABASE = conf["project-database"]["name"]


MASSES = [13,15,16,17,18,24,25,26,27,29,30,31,37,38,41,42,43,44,45]+[i for i in range(48,101)]

def run_query(sql):
    """Run sql query"""
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    connection.close()

def add_receptor_coloc(row):
    """
    Insert one record to public.data_receptor_coloc
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO data_receptor_coloc
    (date, id_site, coloc, value) 
    VALUES('{row[0]}' , {row[1]}, '{row[2]}', {row[3]});
    """
    run_query(sql)


def get_files():
    session = requests.session()
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    res = session.request('PROPFIND', 'https://sharebox.lsce.ipsl.fr/public.php/webdav/', allow_redirects=False, headers=headers, verify=False, auth=('Sr49FG4AzSjcHJZ', ''))
    tree = xml.fromstring(res.content)

    File = namedtuple('File', ['name', 'size', 'mtime', 'ctime', 'contenttype'])

    def prop(elem, name, default=None):
        child = elem.find('.//{DAV:}' + name)
        return default if (child is None or child.text is None) else child.text


    def elem2file(elem):
        return File(
            prop(elem, 'href'),
            int(prop(elem, 'getcontentlength', 0)),
            prop(elem, 'getlastmodified', ''),
            prop(elem, 'creationdate', ''),
            prop(elem, 'getcontenttype', ''),
        )
    
    L = [elem2file(elem).name.split('/')[-1] for elem in tree.findall('{DAV:}response')[2:]]
    return(L)


def get_files_from_OC(id_site, start_date, end_date):
    """
    startdate and enddate should be STRINGS in format YYYYmmddHHMM , example for 2020/10/20 at 15:34 --> '202010201534'
    """
    start_date_file = start_date.strftime('%Y%m%d%H%M')
    end_date_file = end_date.strftime('%Y%m%d%H%M')
    L = get_files()
    files = [i for i in L if i.split('_')[3][:-4]<=end_date_file and i.split('_')[3][:-4]>=start_date_file]
    dfs = []
    dfs_receptor_data = []

    ## Get all receptor data
    sql = f"""SELECT DISTINCT A1.date 
            FROM public.data_receptor A1
                LEFT JOIN public.data_receptor_coloc A2 ON A1.date = A2.date
            WHERE A1.date >= '{start_date}' AND A1.date < '{end_date}'
                AND A2.date IS NULL"""
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df_dates = sqlio.read_sql_query(sql, connection)
    connection.close()

    df_dates['date'] = [datetime.fromtimestamp(int(str(date.astype(datetime))[:-9])) for date in df_dates['date'].values]

    ## Get all exogeneous data
    df_global = None
    for file in files:
        if 'raw' in file:
            df = pd.read_csv(f'https://sharebox.lsce.ipsl.fr/index.php/s/Sr49FG4AzSjcHJZ/download?path=%2F&files={file}', header=None, sep=' ') 
            df = df[[1, 2, 30, 59]].rename(columns={1:'date', 2:'hour', 30:'BB', 59:'BC7'})
            df['BCwb'] = [a*b/100 * (1/1000) for (a,b) in zip(df['BC7'].values,df['BB'].values)]
            df['BCff'] = [a/1000 - b for (a,b) in zip(df['BC7'].values, df['BCwb'].values)]
            df['date'] = [datetime.strptime(date.split('\t')[-1] + " " + hour, "%Y/%m/%d %H:%M:%S") for (date, hour) in zip(df['date'].values, df['hour'].values)]
        
            if df_global is None:
                df_global = df.copy()
            else:
                df_global = df_global.append(df, ignore_index=True, verify_integrity=True)

    ## Create exogeneous data with time granularity of receptor data
    for date in df_dates.values:
        df_filter = df_global[(df_global['date'] < date[0]) & (df_global['date'] >= (date[0] - np.timedelta64(30, 'm')))]
        df_filter = np.mean(df_filter)
        row_coloc_BCwb = [datetime.fromtimestamp(int(str(date[0].astype(datetime))[:-9])).strftime('%Y-%m-%d %H:%M:%S'), id_site, 'BCwb', df_filter['BCwb']]
        row_coloc_BCff = [datetime.fromtimestamp(int(str(date[0].astype(datetime))[:-9])).strftime('%Y-%m-%d %H:%M:%S'), id_site, 'BCff', df_filter['BCff']]
        
        try:
            print(row_coloc_BCwb)
            add_receptor_coloc(row_coloc_BCwb)
        except:
            print(f'BCwb results for datetime :{date[0]} already in table')

        try:
            print(row_coloc_BCff)
            add_receptor_coloc(row_coloc_BCff)
        except:
            print(f'BCff results for datetime :{date[0]} already in table')

    return (dfs, dfs_receptor_data)


if __name__ == '__main__':
    dfs, dfs_receptor_data = get_files_from_OC(1, (datetime.now()-timedelta(days=4)), (datetime.now() + timedelta(days=1)))
    print("Done")