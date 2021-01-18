# known useful libraries
import os
import re
import pandas as pd
import numpy as np
import time
# handling postgres database
import psycopg2
import pandas.io.sql as sqlio
from queries import *
# regressors
from sklearn.linear_model import Lasso
from sklearn import metrics
import scipy.odr



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

def run_lasso(date, profiles):
    """
    Take one date and a list of profiles and return contribution of each of the profiles of the sample of selected date using Lasso 
    date in format : YYYY-mm-dd HH:00:00
    it returns two lists : the first one stores contributions and the second the standard deviations (for lasso we will have null in std)
    """
    # get sample from db
    sql = f"SELECT * FROM public.data_receptor where date = '{date}' order by mass;"
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df_receptor_data = sqlio.read_sql_query(sql, connection)
    connection.close()
    df_receptor_data = df_receptor_data[df_receptor_data.columns[2:]]
    value, uncertainty = get_profiles(profiles)

    X_train = value[profiles].values
    y_train = df_receptor_data['value'].values.reshape(-1,1)

    alpha = 0.0001
    lasso = Lasso(fit_intercept=False, alpha=alpha, positive=True)     # We train without intercept and we shoose to have only positive values
    lasso.fit(X_train, y_train)                                        #training the algorithm  
    return(lasso.coef_ , [None for i in lasso.coef_])
    # return(y_train)


def run_odr(date, profiles, lasso=[]):
    """
    Take one date and a list of profiles and return contribution of each of the profiles of the sample of selected date using Lasso 
    date in format : YYYY-mm-dd HH:00:00
    it returns two lists : the first one stores contributions and the second the standard deviations
    """
    # get sample from db
    sql = f"SELECT * FROM public.data_receptor where date = '{date}' order by mass;"
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df_receptor_data = sqlio.read_sql_query(sql, connection)
    connection.close()
    df_receptor_data = df_receptor_data[df_receptor_data.columns[2:]]
    value, uncertainty = get_profiles(profiles)

    # we need lasso results because it assists ODR to converge
    if len(lasso)==0:
        lasso = run_lasso(date, profiles)[0]

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

def get_dates(year_month):
    """
    get dates in db for a selected month of a year
    year_month should be in the following format : YYYY-mm
    """
    # 
    sql = f"SELECT to_char(date, 'YYYY-MM-DD HH24:00:00') FROM(SELECT date FROM public.data_receptor WHERE to_char(date, 'YYYY-MM') = '{year_month}' GROUP BY 1 ORDER BY 1 DESC) AS foo;"
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df_dates = sqlio.read_sql_query(sql, connection)
    connection.close()
    if len(df_dates.T.values)==0:
        return([])
    dates = df_dates.T.values[0]
    return(dates)


def get_dates_regressor_results(year_month):
    """
    get dates in db for a selected month of a year
    year_month should be in the following format : YYYY-mm
    """
    # 
    sql = f"SELECT to_char(date, 'YYYY-MM-DD HH24:00:00') FROM(SELECT date FROM public.regressor_results WHERE to_char(date, 'YYYY') = '{year_month}' GROUP BY 1 ORDER BY 1 DESC) AS foo;"
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    df_dates = sqlio.read_sql_query(sql, connection)
    connection.close()
    if len(df_dates.T.values)==0:
        return([])
    dates = df_dates.T.values[0]
    return(dates)



def compute_store_regressor(date, id_site, id_analysis, profiles=['BBOA', 'HOA', 'LO-OOA', 'MO-OOA']):
    """
    compute lasso and odr result for one year and store them in a table
    """
    dates = get_dates(date)
    print(f"We have {len(dates)} dates")
    for i in dates:
        print(i)
        lasso = run_lasso(i, profiles)
        odr = run_odr(i, profiles, lasso=lasso[0])
        for indx, profile in enumerate(profiles):
            print(profile)
            row_lasso = [i, id_site, id_analysis, 'LASSO', profile, lasso[0][indx], 'Null']
            row_odr = [i, id_site, id_analysis, 'ODR', profile, odr[0][indx], odr[1][indx]]
            add_2_regressor_results(row_lasso)
            add_2_regressor_results(row_odr)
            print(row_lasso)
            print(row_odr)

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
    sql = f"SELECT * FROM public.data_receptor where date = '{date}' order by mass;"
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
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


def compute_store_errors(date, id_site, id_analysis):
    """
    compute lasso and odr result for one year and store them in a table
    """
    dates = get_dates_regressor_results(date)
    print(f"We have {len(dates)} dates")
    for i in dates:
        print(i)
        for model in ['LASSO', 'ODR', 'PMF']:
            print(model)
            df_signal_recons = compute_signal_reconst(i, model, id_site, id_analysis)
            if len(df_signal_recons)==0:
                print(f"df_signal_recons empty")
                continue
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
            # for row in df_signal_recons.values:
            #     print(row)
            #     add_2_signal_recons(row)

            for error_type in ['MSE', 'MAE']:
                print(error_type)
                df_error = get_error(i, model, id_site, id_analysis, error_type, df_signal_recons=df_signal_recons)
                if len(df_error)==0:
                    print(f"df_error empty")
                    continue
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
                # for row in df_error.values:
                #     print(row)
                #     add_2_model_error(row)


def compute_show_errors(date, model, error_types, id_site, id_analysis):
    """
    compute lasso and odr result for one date and show them for debug
    error_types must be a list of error_types, if only one error to test : [error_to_test]
    """
    dates = [date]
    print(f"We have {len(dates)} dates")
    for i in dates:
        print(i)
        for model in [model]:
            print(model)
            df_signal_recons = compute_signal_reconst(i, model, id_site, id_analysis)
            print(df_signal_recons)
            if len(df_signal_recons)==0:
                print(f"df_error empty")
                continue


            for error_type in error_types:
                print(error_type)
                df_error = get_error(i, model, id_site, id_analysis, error_type, df_signal_recons=df_signal_recons)
                print(df_error)



def get_error_debug(date, model, id_site, id_analysis, error_type, df_signal_recons=[]):
    sql = f"SELECT * FROM public.data_receptor where date = '{date}' order by mass;"
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
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


    





if __name__ == "__main__":
    # compute_store_regressor("2018-02", 1, 1)
    compute_store_errors("2014", 1, 1)
    # compute_show_errors("2018-03-17 04:00:00", "PMF", ['MAE'], 1, 1)
    # print(get_error_debug('2016-06-17 14:00:00', "LASSO", 1, 1, 'MSE'))
    # print(compute_signal_reconst('2016-06-17 14:00:00', 'ODR', 1, 1))
    # print(get_error('2016-06-17 14:00:00', 'LASSO', 1, 1, 'MAE'))
    # print(compute_signal_reconst())