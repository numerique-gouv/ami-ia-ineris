# handling postgres database
import psycopg2
import pandas.io.sql as sqlio



# Credentails#####################################
USER = ""
HOSTNAME = ""
PASSWORD = ""
PORT = ""
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


QUERY_TABLE_MOLECULES = """
-- Table: public.molecules
-- DROP TABLE public.molecules;
CREATE TABLE public.molecules IF NOT EXISTS
(
    id_molecule integer NOT NULL,
    molecule_name text NOT NULL,
    cas text,
    formula text,
    mass numeric NOT NULL,
    retention_time numeric,
    upload_date timestamp,
    source text NOT NULL,
    CONSTRAINT molecules_pkey PRIMARY KEY (id_molecule)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.molecules
    OWNER to "ineris";
"""

def add_2_molecules(row):
    """
    Insert one record to public.molecules
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO molecules 
    (id_molecule, molecule_name, cas, formula, mass, retention_time, upload_date, source) 
    VALUES({row[0]} , '{row[1]}' , '{row[2]}' , '{row[3]}' , {row[4]}, {row[5]}, '{row[6]}', '{row[7]}');
    """
    run_query(sql)



QUERY_TABLE_ANALYSIS = """
-- Table: public.analysis
-- DROP TABLE public.analysis;
CREATE TABLE public.analysis IF NOT EXISTS
(
    id_analysis integer NOT NULL,
    date_analysis timestamp NOT NULL,
    threshold_positif numeric NOT NULL,
    threshold_negatif numeric NOT NULL,
    mz_tolerance numeric NOT NULL,
    rt_tolerance numeric NOT NULL,
    treatment_duration numeric NOT NULL,
    analysis_state varchar(10) NOT NULL,
    CONSTRAINT molecules_pkey PRIMARY KEY (id_analysis)
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
    (id_analysis, date_analysis, threshold_positif, threshold_negatif, mz_tolerance, rt_tolerance, treatment_duration, analysis_state) 
    VALUES({row[0]} , '{row[1]}' , {row[2]} , {row[3]} , {row[4]}, {row[5]}, {row[6]}, '{row[7]}');
    """
    run_query(sql)




QUERY_TABLE_MZML_CHROMATO = """
-- Table: public.mzml_chromato
-- DROP TABLE public.mzml_chromato;
CREATE TABLE public.mzml_chromato IF NOT EXISTS
(
    id_mzml integer NOT NULL,
    time numeric NOT NULL,
    tic numeric NOT NULL,
    CONSTRAINT molecules_pkey PRIMARY KEY (id_mzml, time)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.mzml_chromato
    OWNER to "ineris";
"""

def add_2_mzml_chromato(row):
    """
    Insert one record to public.mzml_chromato
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO mzml_chromato 
    (id_mzml, time, tic) 
    VALUES({row[0]} , {row[1]} , {row[2]});
    """
    run_query(sql)



QUERY_TABLE_SEARCH_MASS_MZML = """
-- Table: public.search_mass_mzml
-- DROP TABLE public.search_mass_mzml;
CREATE TABLE public.search_mass_mzml IF NOT EXISTS
(
    id_mzml integer NOT NULL,
    id_molecule integer NOT NULL,
    id_analysis integer NOT NULL,
    time numeric NOT NULL,
    tic numeric NOT NULL,
    tic_rt numeric NOT NULL,
    CONSTRAINT molecules_pkey PRIMARY KEY (id_mzml, id_molecule, id_analysis, time)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.search_mass_mzml
    OWNER to "ineris";
"""

def add_2_search_mass_mzml(row):
    """
    Insert one record to public.search_mass_mzml
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO search_mass_mzml 
    (id_mzml, id_molecule, id_analysis, time, tic, tic_rt) 
    VALUES({row[0]} , {row[1]} , {row[2]}, {row[3]}, {row[4]}, {row[5]});
    """
    run_query(sql)





QUERY_TABLE_EXTRACTED_PEAKS = """
-- Table: public.extracted_peaks
-- DROP TABLE public.extracted_peaks;
CREATE TABLE public.extracted_peaks IF NOT EXISTS
(
    id_mzml integer NOT NULL,
    id_molecule integer NOT NULL,
    id_analysis integer NOT NULL,
    mass_exp numeric NOT NULL,
    retention_time_exp numeric NOT NULL,
    tic numeric NOT NULL,
    id_spec_scan integer NOT NULL,
    id_spec_frag_10 integer,
    id_spec_frag_20 integer,
    id_spec_frag_40 integer,
    CONSTRAINT molecules_pkey PRIMARY KEY (id_mzml, id_molecule, id_analysis)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.extracted_peaks
    OWNER to "ineris";
"""

def add_2_extracted_peaks(row):
    """
    Insert one record to public.extracted_peaks
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO extracted_peaks 
    (id_mzml, id_molecule, id_analysis, mass_exp, retention_time_exp, tic, id_spec_scan, id_spec_frag_10, id_spec_frag_20, id_spec_frag_40) 
    VALUES({row[0]} , {row[1]} , {row[2]}, {row[3]}, {row[4]}, {row[5]}, {row[6]}, {row[7]}, {row[8]}, {row[9]});
    """
    run_query(sql)




QUERY_TABLE_ISOTOPIC_PROFILE = """
-- Table: public.isotopic_profile
-- DROP TABLE public.isotopic_profile;
CREATE TABLE public.isotopic_profile IF NOT EXISTS
(
    id_mzml integer NOT NULL,
    id_molecule integer NOT NULL,
    id_analysis integer NOT NULL,
    retention_time_exp numeric NOT NULL,
    id_spec_scan integer,
    mz_exp numeric NOT NULL,
    tic_exp numeric NOT NULL,
    mz_theoric numeric NOT NULL,
    tic_theoric numeric NOT NULL,
    CONSTRAINT molecules_pkey PRIMARY KEY (id_mzml, id_molecule, id_analysis, retention_time_exp, mz_theoric)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.isotopic_profile
    OWNER to "ineris";
"""

def add_2_isotopic_profile(row):
    """
    Insert one record to public.isotopic_profile
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO isotopic_profile 
    (id_mzml, id_molecule, id_analysis, retention_time_exp, id_spec_scan, mz_exp, tic_exp, mz_theoric, tic_theoric) 
    VALUES({row[0]} , {row[1]} , {row[2]}, {row[3]}, {row[4]}, {row[5]}, {row[6]}, {row[7]}, {row[8]});
    """
    run_query(sql)




QUERY_TABLE_FRAGMENT = """
-- Table: public.fragment
-- DROP TABLE public.fragment;
CREATE TABLE public.fragment IF NOT EXISTS
(
    id_mzml integer NOT NULL,
    id_molecule integer NOT NULL,
    id_analysis integer NOT NULL,
    collision_energy numeric NOT NULL,
    id_spec integer,
    mz_exp numeric NOT NULL,
    tic_exp numeric NOT NULL,
    mz_theoric numeric NOT NULL,
    tic_theoric numeric NOT NULL,
    CONSTRAINT molecules_pkey PRIMARY KEY (id_mzml, id_molecule, id_analysis, collision_energy, mz_theoric)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.fragment
    OWNER to "ineris";
"""

def add_2_fragment(row):
    """
    Insert one record to public.fragment
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO fragment 
    (id_mzml, id_molecule, id_analysis, collision_energy, id_spec, mz_exp, tic_exp, mz_theoric, tic_theoric) 
    VALUES({row[0]} , {row[1]} , {row[2]}, {row[3]}, {row[4]}, {row[5]}, {row[6]}, {row[7]}, {row[8]});
    """
    run_query(sql)


QUERIES = [QUERY_TABLE_MZML_FILES, QUERY_TABLE_MOLECULES, QUERY_TABLE_ANALYSIS, QUERY_TABLE_MZML_CHROMATO, QUERY_TABLE_SEARCH_MASS_MZML, 
           QUERY_TABLE_EXTRACTED_PEAKS, QUERY_TABLE_ISOTOPIC_PROFILE, QUERY_TABLE_FRAGMENT]