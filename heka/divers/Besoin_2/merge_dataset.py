import psycopg2
import pandas as pd
import pandas.io.sql as sqlio
from sqlalchemy import create_engine



USER = ""
HOSTNAME = ""
PASSWORD = ""
PORT = "5432"
DATABASE = ""

# get data emission
connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
sql = f"""SELECT * FROM public.epa_emission_normalisation;"""
data_emission = sqlio.read_sql_query(sql, connection)
connection.close()

# get data bruit de fond
connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
sql = f"""SELECT * FROM public.epa_bdf_normalisation;"""
data_bdf = sqlio.read_sql_query(sql, connection)
connection.close()


# create ans put column id in the begining of df_emission
data_emission['id'] = data_emission['file'] + '_' +data_emission['test date'] + '_' + data_emission['run id']
first_col = data_emission.pop('id')
data_emission.insert(0, 'id', first_col)


# create ans put column id in the begining of df_bdf
data_bdf['id'] = data_bdf['Site'] +'_'+ data_bdf['Site #'].astype(str)
first_col = data_bdf.pop('id')
data_bdf.insert(0, 'id', first_col)

# extract same columns
columns = ['id', '2378-TCDD_A', '12378-PeCDD_A', '123478-HxCDD_A', '123678-HxCDD_A', '123789-HxCDD_A', '1234678-HpCDD_A', 'OCDD_A', '2378-TCDF_A', '12378-PeCDF_A', '23478-PeCDF_A', '123478-HxCDF_A', '123678-HxCDF_A', '234678-HxCDF_A', '123789-HxCDF_A', '1234678-HpCDF_A', '1234789-HpCDF_A', 'OCDF_A', '2378-TCDD_C', '12378-PeCDD_C', '123478-HxCDD_C', '123678-HxCDD_C', '123789-HxCDD_C', '1234678-HpCDD_C', 'OCDD_C', '2378-TCDF_C', '12378-PeCDF_C', '23478-PeCDF_C', '123478-HxCDF_C', '123678-HxCDF_C', '234678-HxCDF_C', '123789-HxCDF_C', '1234678-HpCDF_C', '1234789-HpCDF_C', 'OCDF_C']
df_bdf = data_bdf[columns]
df_emission = data_emission[columns]

# create label for each datafrme and concatenate both
df_bdf['label'] = 'bdf'
df_emission['label'] = 'emission'
data_final = pd.concat([df_emission, df_bdf], ignore_index=True)


# put the dataframe in the database
engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')
data_final[:0].to_sql('bdd_emission_bdf', engine, if_exists='replace',index=False)
data_final.to_sql('bdd_emission_bdf', engine, if_exists='append',index=False)
