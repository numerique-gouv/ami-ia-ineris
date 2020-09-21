# handling postgres database
import psycopg2
import pandas.io.sql as sqlio
import pandas as pd 
from sqlalchemy import create_engine


PATH_PROFILE = 'C:\\Users\\alahssini\\Desktop\\INERIS\\Besoin3\\Data\\4_Factors_Averaged_factor_Mass_Spectra.csv'
PATH_ACSM = 'C:\\Users\\alahssini\\Desktop\\INERIS\\Besoin3\\Data\\data_brute.csv'


#read df, the df may contain 9 columns : amus,BBOA_mean,BBOA_standard_dev,HOA_mean,HOA_standard_dev,LO-OOA_mean,LO-OOA_standard_dev,MO-OOA_mean,MO-OOA_standard_dev
df_profile = pd.read_csv(PATH_PROFILE)


#Clean the dataframe
def clean(x):
    s=x.replace(',','.')
    s=float(s)
    return(s)



df_profile['BBOA_mean']=df_profile['BBOA_mean'].apply(lambda x: clean(x))
df_profile['BBOA_standard_dev']=df_profile['BBOA_standard_dev'].apply(lambda x: clean(x))
df_profile['HOA_mean']=df_profile['HOA_mean'].apply(lambda x: clean(x))
df_profile['HOA_standard_dev']=df_profile['HOA_standard_dev'].apply(lambda x: clean(x))
df_profile['LO-OOA_mean']=df_profile['LO-OOA_mean'].apply(lambda x: clean(x))
df_profile['LO-OOA_standard_dev']=df_profile['LO-OOA_standard_dev'].apply(lambda x: clean(x))
df_profile['MO-OOA_mean']=df_profile['MO-OOA_mean'].apply(lambda x: clean(x))
df_profile['MO-OOA_standard_dev']=df_profile['MO-OOA_standard_dev'].apply(lambda x: clean(x))



df = pd.read_csv(PATH_ACSM)

for i in df.columns[1:]:
    df[i] = df[i].apply(lambda x: clean(x))

df['acsm_time_utc_end'] =  pd.to_datetime(df['acsm_time_utc_end'], format='%d/%m/%Y %H:%M').dt.strftime('%Y-%m-%d %H:00:00')


# Credentails#####################################
USER =  ""
HOSTNAME = ""
PASSWORD = ""
PORT = "5432"
DATABASE = ""
##################################################


def run_query(sql):
    """Run sql query"""
    connection = psycopg2.connect(user = USER, password = PASSWORD, host = HOSTNAME, port = PORT, database = DATABASE)
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()
    connection.close()


QUERY_TABLE_MZML_FILES = """
-- Table: public.mzml_files
-- DROP TABLE public.mzml_files;
CREATE TABLE public.mzml_files IF NOT EXISTS
(
    id_mzml integer NOT NULL,
    mzml_file text NOT NULL,
    ionisation varchar(3) NOT NULL,
    acquisition_mode varchar(6) NOT NULL,
    spectrum_number integer NOT NULL,
    upload_date timestamp,
    sampling_site text,
    sampling_date timestamp, 
    CONSTRAINT mzml_files_pkey PRIMARY KEY (id_mzml)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.mzml_files
    OWNER to "ineris";
"""

def add_2_mzml_files(row):
    """
    Insert one record to public.mzml_files
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO mzml_files 
    (id_mzml, mzml_file, ionisation, acquisition_mode, spectrum_number, upload_date, sampling_site, sampling_date) 
    VALUES({row[0]} , '{row[1]}' , '{row[2]}' , '{row[3]}' , {row[4]}, '{row[5]}', '{row[6]}', '{row[7]}');
    """
    run_query(sql)


if __name__ == '__main__':
    # put the dataframe in the database
    engine = create_engine(f'postgresql://{USER}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}')
    df[:0].to_sql('sirta_brute', engine, if_exists='replace',index=False)
    df.to_sql('sirta_brute', engine, if_exists='append',index=False)