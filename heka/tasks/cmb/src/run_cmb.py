# known useful libraries
import os
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


conf = yaml.load(os.environ["PROJECT_CONFIG"], Loader=yaml.SafeLoader)


USER = conf["project-database"]["user"]
PASSWORD = conf["project-database"]["password"]
HOSTNAME = conf["project-database"]["hostname"]
PORT = "5432"
DATABASE = conf["project-database"]["name"]


MASSES = [13,15,16,17,18,24,25,26,27,29,30,31,37,38,41,42,43,44,45]+[i for i in range(48,101)]


def get_files():
    session = requests.session()
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    res = session.request('PROPFIND', 'https://sharebox.lsce.ipsl.fr/public.php/webdav/', allow_redirects=False, headers=headers, verify=False, auth=('ic4cehvKfKJTQVk', ''))
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
    L.remove('')
    return(L)

def get_files_from_OC(start_date, end_date):
    """
    startdate and enddate should be STRINGS in format YYYYmmddHHMM , example for 2020/10/20 at 15:34 --> '202010201534'
    """
    L = get_files()
    files = [i for i in L if i.split('_')[3][:-4]<=end_date and i.split('_')[3][:-4]>=start_date]
    dfs = []
    dfs_receptor_data = []
    for file in files:
        print(file)
        for sep in [',', ';', '\t']:
            df = pd.read_csv(f'https://sharebox.lsce.ipsl.fr/index.php/s/ic4cehvKfKJTQVk/download?path=%2F&files={file}', sep=sep)
            if len(df.columns) > 1:
                break
        
        data_column_name = df.columns[0]
        df.fillna(df[data_column_name].iloc[0], inplace=True)
        try:
            df[data_column_name] =  pd.to_datetime(df[data_column_name], format='%d/%m/%Y %H:%M:%S').dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            print("No date normalization")
        df = df[df.amus.isin(MASSES)].reset_index(drop=True)
        df['id_site']=1
        df_for_database = df[[data_column_name, 'id_site', 'amus', 'Org_Specs', 'OrgSpecs_err']].rename(columns={data_column_name:'date', 'amus':'mass', 'Org_Specs':'value', 'OrgSpecs_err':'uncertainty'})

        try:
            # put df in the database
            engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

            # Prepare data
            output = StringIO()
            df_for_database.to_csv(output, sep='\t', header=False, index=False)
            output.seek(0)

            # Insert data
            connection = engine.raw_connection()
            cursor = connection.cursor()
            cursor.copy_from(output, 'data_receptor', sep="\t", null='')
            connection.commit()
            cursor.close()
        except:
            print(f'Datetime : {df_for_database.date.values[0]} already in table data_receptor')
        df_receptor_data = df[['amus', 'Org_Specs']].rename(columns={'amus':'mass', 'Org_Specs':'value'})
        dfs.append(df)
        dfs_receptor_data.append(df_receptor_data)

    return(dfs, dfs_receptor_data)



def run_query(sql):
    """Run sql query"""
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    connection.close()

def get_profiles(profiles=['BBOA', 'HOA', 'LO-OOA', 'MO-OOA']):
    """
    Get means and std of profiles from db
    profiles : is a list of profile names.
    """
    # get data from db
    sql = f'SELECT * FROM public.profiles where profile in {tuple(profiles)} order by profile, mass;'
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df = sqlio.read_sql_query(sql, connection)
    connection.close()
    df = df[df.columns[1:]]
    # put data on right format
    df_pivot = df.pivot(index='mass', columns='profile', values=['value', 'uncertainty'])
    # split to value and uncertainty
    value = df_pivot['value'].reset_index()
    uncertainty = df_pivot['uncertainty'].reset_index()
    return(value, uncertainty)


def run_lasso(df, profiles):
    """
    Take one date and a list of profiles and return contribution of each of the profiles of the sample of selected date using Lasso 
    date in format : YYYY-mm-dd HH:00:00
    it returns two lists : the first one stores contributions and the second the standard deviations (for lasso we will have null in std)
    """
    # get sample from db
    df_receptor_data = df[['amus', 'Org_Specs']].rename(columns={'amus':'mass', 'Org_Specs':'value'})
    value, uncertainty = get_profiles(profiles)
    X_train = value[profiles].values
    y_train = df_receptor_data['value'].values.reshape(-1,1)
    alpha = 0.0001
    lasso = Lasso(fit_intercept=False, alpha=alpha, positive=True)     # We train without intercept and we shoose to have only positive values
    lasso.fit(X_train, y_train)                                        #training the algorithm  
    return(lasso.coef_ , [None for i in lasso.coef_])
    # return(y_train)


def run_lasso_lissage(df, profiles, nb_lissage):
    # get sample from db
    if "acsm_utc_time" in df.columns:
        data_column_name = "acsm_utc_time"
    else:
        data_column_name = "ACSM_time"
    date = df[data_column_name].iloc[0]
    print(date)
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    query_date = f"SELECT DISTINCT date FROM public.data_receptor where date <= '{date}' and date >= date '{date}' - interval '2 hour' ORDER BY date DESC LIMIT 3"
    df_date = sqlio.read_sql_query(query_date, connection)

    if len(df_date) < 3:
        print(f'Datetime : {date} not possible - lack of samples')
        connection.close()
        return None
    else:
        value, uncertainty = get_profiles(profiles)
        value = value.rename(columns={"mass" : "amus"})

        ## Collect the receptor data
        sql = f"""SELECT * FROM public.data_receptor where date = '{date}' """
        for k in range(1, nb_lissage):
            date_intemediaire = df_date.iloc[k, 0]
            sql += f"or date = '{date_intemediaire}'"
        sql += "order by mass;"
        df_receptor_data = sqlio.read_sql_query(sql, connection)
        df_receptor_data = df_receptor_data[df_receptor_data.columns]

        cor = value.merge(df_receptor_data, left_on='amus', right_on='mass').drop(columns=['mass', 'amus'])

        # Choose variables
        X_train = cor[profiles].values
        y_train = cor['value'].values.reshape(-1,1)

        # Training Lasso Model
        alpha = 0.0001
        lasso = Lasso(fit_intercept=False, alpha=alpha)
        lasso.fit(X_train, y_train)
                             
        connection.close()
        return(lasso.coef_ , [None for i in lasso.coef_])

def run_odr(df, profiles, lasso=[]):
    """
    Take one date and a list of profiles and return contribution of each of the profiles of the sample of selected date using Lasso 
    date in format : YYYY-mm-dd HH:00:00
    it returns two lists : the first one stores contributions and the second the standard deviations
    """
    # get sample from db
    df_receptor_data = df[['amus', 'Org_Specs']].rename(columns={'amus':'mass', 'Org_Specs':'value'})
    value, uncertainty = get_profiles(profiles)
    # we need lasso results because it assists ODR to converge
    if len(lasso)==0:
        lasso = run_lasso(df, profiles)[0]
    def linfit(beta, x):
        return beta[0]*x[0] + beta[1]*x[1] + beta[2]*x[2] + beta[3]*x[3]
    y = np.array(df_receptor_data['value'].values, dtype='float')
    x = np.array(value[profiles].T.values, dtype='float')
    wd = np.array(uncertainty[profiles].T.values, dtype='float')
    linmod = scipy.odr.Model(linfit)
    # data = scipy.odr.Data(x, y, wd=wd)
    data = scipy.odr.RealData(x, y, sx=wd)
    odrfit = scipy.odr.ODR(data, linmod, beta0=lasso)
    odrres = odrfit.run()
    return(odrres.beta, odrres.sd_beta)

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


def compute_store_regressor(id_site, id_analysis, profiles=['BBOA', 'HOA', 'LO-OOA', 'MO-OOA']):
    """
    compute lasso and odr result for one year and store them in a table
    """
    lasso = run_lasso(df, profiles)
    odr = run_odr(df, profiles, lasso=lasso[0])
    lasso_lissage = run_lasso_lissage(df, profiles, 3)
    for indx, profile in enumerate(profiles):
        print(profile)
        
        if "acsm_utc_time" in df.columns:
            data_column_name = "acsm_utc_time"
        else:
            data_column_name = "ACSM_time"

        row_lasso = [df[data_column_name].iloc[0], id_site, id_analysis, 'LASSO', profile, lasso[0][indx], 'Null']
        row_odr = [df[data_column_name].iloc[0], id_site, id_analysis, 'ODR', profile, odr[0][indx], odr[1][indx]]
        try:
            print(row_lasso)
            add_2_regressor_results(row_lasso)
        except:
            print(f'Lasso results for datetime :{df[data_column_name].iloc[0]} already in table')
        try:
            print(row_odr)
            add_2_regressor_results(row_odr)
        except:
            print(f'ODR results for datetime :{df[data_column_name].iloc[0]} already in table')          
        try:
            row_lasso_lissage = [df[data_column_name].iloc[0], id_site, id_analysis, 'LASSO_x3', profile, lasso_lissage[0][indx], 'Null']
            print(row_lasso_lissage)
            add_2_regressor_results(row_lasso_lissage)
        except:
            print(f'Lasso X3 results for datetime :{df[data_column_name].iloc[0]} already in table')  



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
    value = get_profiles()[0]
    df_melt = pd.melt(frame=value, id_vars='mass', value_vars=['BBOA', 'HOA', 'LO-OOA', 'MO-OOA'], var_name="profile", value_name="value")
    df_join = df.merge(df_melt,how='left',left_on=['profile'],right_on=['profile'])
    df_join['value'] = df_join['contribution']*df_join['value']
    df_join = df_join.groupby(['date', 'id_site', 'id_analysis', 'model', 'mass']).sum().reset_index()[['date', 'id_site', 'id_analysis', 'model', 'mass', 'value']]
    return(df_join)


def get_error(date, model, id_site, id_analysis, error_type, df_signal_recons=[]):
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    if model == 'LASSO_x3':
        query_date = f"SELECT DISTINCT date FROM public.data_receptor where date <= '{date}' and date >= date '{date}' - interval '2 hour' ORDER BY date DESC LIMIT 3"
        df_date = sqlio.read_sql_query(query_date, connection)
        if len(df_date) == 3:
            sql = f"""WITH aux AS(
                SELECT *
                FROM public.data_receptor
                WHERE date IN (
                    SELECT DISTINCT date
                    FROM public.data_receptor
                    WHERE date = '{date}' OR (date + interval '2 hour'>= '{date}'  AND date <= '{date}')
                    ORDER BY date DESC
                    LIMIT 3)
                )
            SELECT max(date) as date, id_site, mass, AVG(value) AS value, AVG(uncertainty) AS uncertainty
            FROM aux
            GROUP BY id_site, mass
            ORDER BY mass;"""
            df_receptor_data = sqlio.read_sql_query(sql, connection)
        else:
            df_receptor_data = pd.DataFrame([])    
    else:
        sql = f"SELECT * FROM public.data_receptor where date = '{date}' order by mass;"
        df_receptor_data = sqlio.read_sql_query(sql, connection)    
    connection.close()

    
    if len(df_receptor_data)==0:
        return([])

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


def compute_store_errors(df, id_site, id_analysis):
    """
    compute lasso and odr result for one year and store them in a table
    """
    if "acsm_utc_time" in df.columns:
        data_column_name = "acsm_utc_time"
    else:
        data_column_name = "ACSM_time"
    date = df[data_column_name].iloc[0]
    for model in ['LASSO', 'ODR', 'LASSO_x3']:
        ## SIGNA RECONSTITUTION
        print(model)
        df_signal_recons = compute_signal_reconst(date, model, id_site, id_analysis)
        if len(df_signal_recons)==0:
            print(f"df_signal_recons empty")
            continue
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


        for error_type in ['MSE', 'MAE']:
            print(error_type)
            df_error = get_error(date, model, id_site, id_analysis, error_type, df_signal_recons=df_signal_recons)
            if len(df_error)==0:
                print(f"df_error empty")
                continue
            try:
                # put df in the database
                engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

                # Prepare data
                output = StringIO()
                df_error.to_csv(output, sep='\t', header=False, index=False)
                output.seek(0)

                # Insert data
                connection = engine.raw_connection()
                cursor = connection.cursor()
                cursor.copy_from(output, 'model_error', sep="\t", null='')
                connection.commit()
                cursor.close()
            except:
                print(f'Errors for {model} in {date} with error type {error_type} already in table')

if __name__ == '__main__':
    dfs, dfs_receptor_data = get_files_from_OC((datetime.datetime.now()-datetime.timedelta(hours=3)).strftime('%Y%m%d%H%M'), (datetime.datetime.now()+datetime.timedelta(days=1)).strftime('%Y%m%d%H%M'))
    for i in range(len(dfs)):
        df = dfs[i]
        df_receptor_data = dfs_receptor_data[i]
        compute_store_regressor(1, 3, profiles=['BBOA', 'HOA', 'LO-OOA', 'MO-OOA'])
        compute_store_errors(df, 1, 3)

    print("Update done !")