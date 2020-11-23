# handling postgres database
import psycopg2
import pandas.io.sql as sqlio
import pandas as pd 
from sqlalchemy import create_engine
from io import StringIO


PATH_PROFILE = 'C:\\Users\\alahssini\\Desktop\\INERIS\\Besoin3\\Data\\4_Factors_Averaged_factor_Mass_Spectra.csv'
PATH_ACSM = 'C:\\Users\\alahssini\\Desktop\\INERIS\\Besoin3\\Data\\data_brute.csv'
PATH_COLOC = 'C:\\Users\\alahssini\\Desktop\\INERIS\\Besoin3\\Data\\donnees_colocalisees_SIRTA.csv'
PATH_PMF_CONTR = 'C:\\Users\\alahssini\\Desktop\\INERIS\\Besoin3\\Data\\PMF_series_temporelles_4_facteurs.csv'

# Credentails#####################################
USER =  ""
HOSTNAME = ""
PASSWORD = ""
PORT = "5432"
DATABASE = ""
##################################################

#Clean the dataframe
def clean(x):
    if not pd.isna(x):
        s=x.replace(',','.')
        s=float(s)
        return(s)

def upload_sirta_profiles(PATH_PROFILE=PATH_PROFILE):
    #read df, the df may contain 9 columns : amus,BBOA_mean,BBOA_standard_dev,HOA_mean,HOA_standard_dev,LO-OOA_mean,LO-OOA_standard_dev,MO-OOA_mean,MO-OOA_standard_dev
    df_profile = pd.read_csv(PATH_PROFILE)

    # clean dataset
    for i in df_profile.columns[1:]:
        df_profile[i] = df_profile[i].apply(lambda x: clean(x))


    #melt datframe from wide to longue
    first_melt = pd.melt(frame=df_profile, id_vars=['amus', 'BBOA_standard_dev', 'HOA_standard_dev', 'LO-OOA_standard_dev', 'MO-OOA_standard_dev'], value_vars=['BBOA_mean', 'HOA_mean', 'LO-OOA_mean', 'MO-OOA_mean'], var_name="profile", value_name="value")
    second_melt = pd.melt(frame=first_melt, id_vars=['amus', 'profile', 'value'], value_vars=['BBOA_standard_dev', 'HOA_standard_dev', 'LO-OOA_standard_dev', 'MO-OOA_standard_dev'], var_name="uncertainty_name", value_name="uncertainty")
    second_melt["profile"] = second_melt["profile"].apply(lambda x: x.replace('_mean', ''))
    second_melt["uncertainty_name"] = second_melt["uncertainty_name"].apply(lambda x: x.replace('_standard_dev', ''))

    # get rid of non sense rows
    pre_df = second_melt[second_melt["uncertainty_name"]==second_melt["profile"]].reset_index(drop=True)[["profile", "amus", "value", "uncertainty"]].rename(columns={"amus": "mass"})
    # create id for profiles as we have only four known profiles
    pre_df['id_profile'] = pre_df['profile'].map({"BBOA":1, "HOA":2, "LO-OOA":3, "MO-OOA":4})
    # put the id in the first place
    first_col = pre_df.pop('id_profile')
    pre_df.insert(0, 'id_profile', first_col)

    # put pre_df in the datbase
    engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')
    # pre_df[:0].to_sql('profiles', engine, if_exists='replace',index=False)
    pre_df.to_sql('profiles', engine, if_exists='append',index=False)

    return(pre_df)


def uplaod_sirta_receptor_data(PATH_ACSM=PATH_ACSM):
    # read df, the df may contain 72 columns : acsm_time_utc_end, and 71 masses from 13 to 100 .
    df = pd.read_csv(PATH_ACSM)
    # clean dataset
    for i in df.columns[1:]:
        df[i] = df[i].apply(lambda x: clean(x))

    # put date column into the iso format
    df['acsm_time_utc_end'] =  pd.to_datetime(df['acsm_time_utc_end'], format='%d/%m/%Y %H:%M').dt.strftime('%Y-%m-%d %H:00:00')
    df.rename(columns={"acsm_time_utc_end":"date"}, inplace=True)

    # melt dtaframe from wide to longue
    df_melted = pd.melt(frame=df, id_vars=["date"], value_vars=df.columns[1:], var_name="mass", value_name="value")
    # as we are loading only data for sirta site the unique id we have is 1 
    df_melted['id_site'] = 1
    # we put the column id_site into the second position
    col = df_melted.pop('id_site')
    df_melted.insert(1, 'id_site', col)
    # for now we don't have uncertainties on receptor data
    df_melted['uncertainty'] = None

    # put df in the database
    engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

    # Prepare data
    output = StringIO()
    df_melted.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)

    # Insert data
    connection = engine.raw_connection()
    cursor = connection.cursor()
    cursor.copy_from(output, 'data_receptor', sep="\t", null='')
    connection.commit()
    cursor.close()

    return(df_melted)


def upload_sirta_coloc_data(PATH_COLOC=PATH_COLOC):
    #read df, the df may contain several columns : acsm_time_utc_end and then all colocolised data
    df_coloc = pd.read_csv(PATH_COLOC)

    # clean dataset
    for i in df_coloc.columns[1:]:
        df_coloc[i] = df_coloc[i].apply(lambda x: clean(x))


    # put date column into the iso format
    df_coloc['acsm_time_utc_end'] =  pd.to_datetime(df_coloc['acsm_time_utc_end'], format='%m/%d/%y %H:%M').dt.strftime('%Y-%m-%d %H:00:00')
    df_coloc.rename(columns={"acsm_time_utc_end":"date"}, inplace=True)

    # melt dtaframe from wide to longue
    df_melted = pd.melt(frame=df_coloc, id_vars=["date"], value_vars=df_coloc.columns[1:], var_name="coloc", value_name="value")

    df_melted["id_site"] = 1
    # we put the column id_site into the second position
    col = df_melted.pop('id_site')
    df_melted.insert(1, 'id_site', col)

    # put df in the database
    engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

    # Prepare data
    output = StringIO()
    df_melted.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)

    # Insert data
    connection = engine.raw_connection()
    cursor = connection.cursor()
    cursor.copy_from(output, 'data_receptor_coloc', sep="\t", null='')
    connection.commit()
    cursor.close()

    return(df_melted)


def upload_sirta_pmf_contrib(PATH_PMF_CONTR=PATH_PMF_CONTR):
    #read df, the df may contain several columns : acsm_time_utc_end and then all colocolised data
    df_pmf_result = pd.read_csv(PATH_PMF_CONTR)

    # clean dataset
    for i in df_pmf_result.columns[2:]:
        df_pmf_result[i] = df_pmf_result[i].apply(lambda x: clean(x))


    # put date column into the iso format
    df_pmf_result['end'] =  pd.to_datetime(df_pmf_result['end'], format='%m/%d/%y %H:%M').dt.strftime('%Y-%m-%d %H:00:00')
    df_pmf_result.rename(columns={"end":"date"}, inplace=True)
    _ = df_pmf_result.pop("start")

    # melt dtaframe from wide to longue
    df_melted = pd.melt(frame=df_pmf_result, id_vars=["date"], value_vars=df_pmf_result.columns[1:], var_name="profile", value_name="value")

    df_melted["id_site"] = 1
    # we put the column id_site into the second position
    col = df_melted.pop('id_site')
    df_melted.insert(1, 'id_site', col)

    df_melted["id_analysis"] = 1
    # we put the column id_analysis into the third position
    col = df_melted.pop('id_analysis')
    df_melted.insert(2, 'id_analysis', col)

    df_melted["model"] = "PMF"
    # we put the column model into the fourth position
    col = df_melted.pop('model')
    df_melted.insert(3, 'model', col)

    df_melted["uncertainty"] = None

    # put df in the database
    engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')

    # Prepare data
    output = StringIO()
    df_melted.to_csv(output, sep='\t', header=False, index=False)
    output.seek(0)

    # Insert data
    connection = engine.raw_connection()
    cursor = connection.cursor()
    cursor.copy_from(output, 'regressor_results', sep="\t", null='')
    connection.commit()
    cursor.close()

    return(df_melted)




def run_query(sql):
    """Run sql query"""
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    connection.close()


QUERY_TABLE_PROFILES = """
-- Table: public.profiles
-- DROP TABLE public.profiles;
CREATE TABLE IF NOT EXISTS public.profiles 
(
    id_profile integer NOT NULL,
    profile text NOT NULL,
    mass numeric NOT NULL,
    value numeric,
    uncertainty numeric,
    CONSTRAINT profiles_pkey PRIMARY KEY (id_profile, mass)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.profiles
    OWNER to "ineris";
"""

def add_2_profiles(row):
    """
    Insert one record to public.profiles
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO profiles 
    (id_profile, profile, mass, value, uncertainty) 
    VALUES({row[0]} , '{row[1]}' , {row[2]} , {row[3]} , {row[4]});
    """
    run_query(sql)



QUERY_TABLE_DATA_RECEPTOR = """
-- Table: public.data_receptor
-- DROP TABLE public.data_receptor;
CREATE TABLE IF NOT EXISTS public.data_receptor 
(
    date timestamp NOT NULL,
    id_site text NOT NULL,
    mass numeric NOT NULL,
    value numeric,
    uncertainty numeric,
    CONSTRAINT data_receptor_pkey PRIMARY KEY (date, id_site, mass)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.data_receptor
    OWNER to "ineris";
"""

def add_2_data_receptor(row):
    """
    Insert one record to public.data_receptor
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO data_receptor 
    (date, id_site, mass, value, uncertainty) 
    VALUES('{row[0]}' , {row[1]} , {row[2]} , {row[3]} , {row[4]});
    """
    run_query(sql)



QUERY_TABLE_DATA_RECEPTOR_COLOC = """
-- Table: public.data_receptor_coloc
-- DROP TABLE public.data_receptor_coloc;
CREATE TABLE IF NOT EXISTS public.data_receptor_coloc 
(
    date timestamp NOT NULL,
    id_site integer NOT NULL,
    coloc text NOT NULL,
    value numeric,
    CONSTRAINT data_receptor_coloc_pkey PRIMARY KEY (date, id_site, coloc)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.data_receptor_coloc
    OWNER to "ineris";
"""

def add_2_data_receptor_coloc(row):
    """
    Insert one record to public.data_receptor_coloc
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO data_receptor_coloc 
    (date, id_site, coloc, value) 
    VALUES('{row[0]}' , {row[1]} , '{row[2]}' , {row[3]});
    """
    run_query(sql)


QUERY_TABLE_SITES = """
-- Table: public.sites
-- DROP TABLE public.sites;
CREATE TABLE IF NOT EXISTS public.sites 
(
    id_site integer NOT NULL,
    site text NOT NULL,
    CONSTRAINT sites_pkey PRIMARY KEY (id_site)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.sites
    OWNER to "ineris";
"""

def add_2_sites(row):
    """
    Insert one record to public.sites
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO sites 
    (id_site, site) 
    VALUES({row[0]} , '{row[1]}');
    """
    run_query(sql)


QUERY_TABLE_ANALYSIS = """
-- Table: public.analysis
-- DROP TABLE public.analysis;
CREATE TABLE IF NOT EXISTS public.analysis 
(
    id_analysis integer NOT NULL,
    date_analysis timestamp NOT NULL,
    CONSTRAINT analysis_pkey PRIMARY KEY (id_analysis)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.analysis
    OWNER to "ineris";
"""

def add_2_analysis(row):
    """
    Insert one record to public.analysis
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO analysis 
    (id_anlysis, date_analysis) 
    VALUES({row[0]} , '{row[1]}');
    """
    run_query(sql)


QUERY_TABLE_REGRESSOR_RESULTS = """
-- Table: public.regressor_results
DROP TABLE public.regressor_results;
CREATE TABLE IF NOT EXISTS public.regressor_results 
(
    date timestamp NOT NULL,
    id_site integer NOT NULL,
    id_analysis integer NOT NULL,
    model varchar(6) NOT NULL,
    profile text NOT NULL,
    contribution numeric,
    uncertainty numeric,
    CONSTRAINT regressor_results_pkey PRIMARY KEY (date, id_site, id_analysis, model, profile)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.regressor_results
    OWNER to "ineris";
"""

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


QUERY_TABLE_MODEL_ERROR = """
-- Table: public.model_error
-- DROP TABLE public.model_error;
CREATE TABLE IF NOT EXISTS public.model_error 
(
    date timestamp NOT NULL,
    id_site integer NOT NULL,
    id_analysis integer NOT NULL,
    model varchar(6) NOT NULL,
    error_type text NOT NULL,
    mass numeric,
    error numeric,
    error_relative numeric,
    CONSTRAINT model_error_pkey PRIMARY KEY (date, id_site, id_analysis, model, error_type, mass)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.model_error
    OWNER to "ineris";
"""

def add_2_model_error(row):
    """
    Insert one record to public.model_error
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO model_error 
    (date, id_site, id_analysis, model, error_type, mass, error) 
    VALUES('{row[0]}' , {row[1]} , {row[2]} , '{row[3]}' , '{row[4]}', {row[5]}, {row[6]});
    """
    run_query(sql)


QUERY_TABLE_SIGNAL_RECONST = """
-- Table: public.signal_reconst
-- DROP TABLE public.signal_reconst;
CREATE TABLE IF NOT EXISTS public.signal_reconst 
(
    date timestamp NOT NULL,
    id_site integer NOT NULL,
    id_analysis integer NOT NULL,
    model varchar(6) NOT NULL,
    mass numeric,
    value numeric,
    CONSTRAINT signal_reconst_pkey PRIMARY KEY (date, id_site, id_analysis, model, mass)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.signal_reconst
    OWNER to "ineris";
"""

def add_2_signal_recons(row):
    """
    Insert one record to public.signal_reconst
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO signal_reconst 
    (date, id_site, id_analysis, model, mass, value) 
    VALUES('{row[0]}' , {row[1]} , {row[2]} , '{row[3]}' , {row[4]}, {row[5]});
    """
    run_query(sql)



if __name__ == '__main__':
    run_query(QUERY_TABLE_SIGNAL_RECONST)
    run_query(QUERY_TABLE_MODEL_ERROR)
    # row = upload_sirta_pmf_contrib()[0:1].values[0]
    # add_2_regressor_results(row)
    # pre_df = upload_sirta_pmf_contrib()
    # print(pre_df)

