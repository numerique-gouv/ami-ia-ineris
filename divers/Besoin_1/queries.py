# handling postgres database
import psycopg2
import pandas.io.sql as sqlio



# Credentails#####################################
USER =  "ineris"
HOSTNAME = ""
PASSWORD = ""
PORT = "5432"
DATABASE = "ineris"
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
CREATE TABLE IF NOT EXISTS public.mzml_files 
(
    id_mzml integer NOT NULL,
    mzml_file text NOT NULL,
    ionisation varchar(3) NOT NULL,
    acquisition_mode varchar(16) NOT NULL,
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
    VALUES({row[0]} , '{row[1]}' , '{row[2]}' , '{row[3]}' , {row[4]}, '{row[5]}', '{row[6]}', {row[7]});
    """
    run_query(sql)


QUERY_TABLE_MOLECULES = """
-- Table: public.molecules
-- DROP TABLE public.molecules;
CREATE TABLE IF NOT EXISTS public.molecules 
(
    id_molecule integer NOT NULL,
    molecule_name text NOT NULL,
    cas text,
    formula text,
    mass numeric NOT NULL,
    retention_time numeric,
    species text,
    ion_polarity text,
    precursor_mz numeric,
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
    (id_molecule, molecule_name, cas, formula, mass, retention_time, species, ion_polarity, precursor_mz, upload_date, source) 
    VALUES({row[0]} , '{row[1]}' , '{row[2]}' , '{row[3]}' , {row[4]}, {row[5]}, '{row[6]}', '{row[7]}', {row[8]}, '{row[9]}', '{row[10]}');
    """
    run_query(sql)




QUERY_TABLE_MOLECULES_BDD_GLOBAL = """
-- Table: public.molecules_bdd_global
-- DROP TABLE public.molecules_bdd_global;
CREATE TABLE IF NOT EXISTS public.molecules_bdd_global 
(
    name text,
    formula text,
    mass numeric,
    retention_time numeric,
    cas text,
    chemspider text,
    numspectra text,
    ccs_count text,
    collision_energy numeric,
    ion_polarity text NOT NULL,
    ion_mode text NOT NULL,
    species text NOT NULL,
    mz numeric NOT NULL,
    intensity numeric NOT NULL,
    precursor_mz numeric NOT NULL,
    source varchar(9) NOT NULL,
    upload_date timestamp,
    CONSTRAINT molecules_bdd_global_pkey PRIMARY KEY (name, species, ion_polarity, collision_energy, mz, source)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.molecules_bdd_global
    OWNER to "ineris";
"""

def add_2_molecules_bdd_global(row):
    """
    Insert one record to public.molecules_bdd_global
    row : list containing all the values of columns of the record
    """
    sql = f"""INSERT INTO molecules_bdd_global 
    (name, formula, mass, retention_time, cas, chemspider, numspectra, ccs_count, collision_energy, ion_polarity, ion_mode, species, mz, intensity, precursor_mz, source, upload_date) 
    VALUES('{row[0]}' , '{row[1]}' , {row[2]} , {row[3]} , '{row[4]}', '{row[5]}', '{row[6]}', '{row[7]}', {row[8]}, '{row[9]}', '{row[10]}', '{row[11]}', {row[12]}, {row[13]}, {row[14]}, '{row[15]}', '{row[16]}');
    """
    run_query(sql)



QUERY_TABLE_ANALYSIS = """
-- Table: public.analysis
-- DROP TABLE public.analysis;
CREATE TABLE IF NOT EXISTS public.analysis 
(
    id_analysis integer NOT NULL,
    date_analysis timestamp NOT NULL,
    threshold_positif numeric NOT NULL,
    threshold_negatif numeric NOT NULL,
    mz_tolerance numeric NOT NULL,
    rt_tolerance numeric NOT NULL,
    treatment_duration varchar(10),
    analysis_state varchar(10),
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
    (id_analysis, date_analysis, threshold_positif, threshold_negatif, mz_tolerance, rt_tolerance, treatment_duration, analysis_state) 
    VALUES({row[0]} , '{row[1]}' , {row[2]} , {row[3]} , {row[4]}, {row[5]}, {row[6]}, {row[7]});
    """
    run_query(sql)




QUERY_TABLE_MZML_CHROMATO = """
-- Table: public.mzml_chromato
-- DROP TABLE public.mzml_chromato;
CREATE TABLE IF NOT EXISTS public.mzml_chromato 
(
    id_mzml integer NOT NULL,
    time numeric NOT NULL,
    tic numeric NOT NULL,
    CONSTRAINT mzml_chromato_pkey PRIMARY KEY (id_mzml, time)
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
CREATE TABLE IF NOT EXISTS public.search_mass_mzml 
(
    id_mzml integer NOT NULL,
    id_molecule integer NOT NULL,
    id_analysis integer NOT NULL,
    time numeric NOT NULL,
    tic numeric NOT NULL,
    tic_rt numeric NOT NULL,
    CONSTRAINT search_mass_mzml_pkey PRIMARY KEY (id_mzml, id_molecule, id_analysis, time)
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
CREATE TABLE IF NOT EXISTS public.extracted_peaks 
(
    id_mzml integer NOT NULL,
    id_molecule integer NOT NULL,
    id_analysis integer NOT NULL,
    mass_exp numeric,
    retention_time_exp numeric NOT NULL,
    tic numeric,
    id_spec_scan integer,
    id_spec_frag_10 integer,
    id_spec_frag_20 integer,
    id_spec_frag_40 integer,
    CONSTRAINT extracted_peaks_pkey PRIMARY KEY (id_mzml, id_molecule, id_analysis, retention_time_exp)
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
CREATE TABLE IF NOT EXISTS public.isotopic_profile
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
    CONSTRAINT isotopic_profile_pkey PRIMARY KEY (id_mzml, id_molecule, id_analysis, retention_time_exp, mz_theoric)
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
CREATE TABLE IF NOT EXISTS public.fragment 
(
    id_mzml integer NOT NULL,
    id_molecule integer NOT NULL,
    id_analysis integer NOT NULL,
    retention_time_exp numeric NOT NULL,
    collision_energy numeric NOT NULL,
    id_spec integer,
    mz_exp numeric NOT NULL,
    tic_exp numeric NOT NULL,
    mz_theoric numeric NOT NULL,
    tic_theoric numeric NOT NULL,
    CONSTRAINT fragment_pkey PRIMARY KEY (id_mzml, id_molecule, id_analysis, retention_time_exp, collision_energy, mz_theoric)
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
    (id_mzml, id_molecule, id_analysis, retention_time_exp, collision_energy, id_spec, mz_exp, tic_exp, mz_theoric, tic_theoric) 
    VALUES({row[0]} , {row[1]} , {row[2]}, {row[3]}, {row[4]}, {row[5]}, {row[6]}, {row[7]}, {row[8]}, {row[9]});
    """
    run_query(sql)


QUERY_TABLE_SIMILARITIES = """
-- Table: public.score_similarities
-- DROP TABLE public.score_similarities;
CREATE TABLE IF NOT EXISTS public.score_similarities 
(
    id_mzml integer,
    id_molecule integer,
    id_analysis integer,
    retention_time_exp numeric,
    tic numeric,
    mass_exp numeric,
    cosine_similarity_10 numeric,
    cosine_similarity_20 numeric,
    cosine_similarity_40 numeric,
    root_similarity_10 numeric,
    root_similarity_20 numeric,
    root_similarity_40 numeric,
    scholle_similarity_10 numeric,
    scholle_similarity_20 numeric,
    scholle_similarity_40 numeric,
    num_fragmentation_the_peaks_10 numeric,
    num_fragmentation_the_peaks_20 numeric,
    num_fragmentation_the_peaks_40 numeric,
    num_fragmentation_exp_peaks_10 numeric,
    num_fragmentation_exp_peaks_20 numeric,
    num_fragmentation_exp_peaks_40 numeric,
    cosine_similarity_isotopic numeric,
    root_similarity_isotopic numeric,
    num_isotopic_the_peaks numeric,
    num_isotopic_exp_peaks numeric,
    cosine_similarity_isotopic_mod numeric,
    retention_time numeric,
    mass numeric,
    CONSTRAINT score_similarities_pkey PRIMARY KEY (id_mzml, id_molecule, id_analysis, retention_time_exp)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.score_similarities
    OWNER to "ineris";
"""


QUERY_TABLE_SCORES = """
-- Table: public.scores
-- DROP TABLE public.scores;
CREATE TABLE IF NOT EXISTS public.scores 
(
    id_mzml integer,
    id_molecule integer,
    id_analysis integer,
    mzml_file text,
    molecule_name text,
    cas text,
    formula text,
    mass numeric,
    source text,
    tic numeric,
    retention_time_exp numeric,
    rt_diff_abs numeric,
    flag_peak_number_exp_20 varchar(3),
    cosine_similarity_20 numeric,
    scholle_similarity_20 numeric,
    flag_peak_number_exp_40 varchar(3),
    cosine_similarity_40 numeric,
    scholle_similarity_40 numeric,
    cosine_similarity_isotopic_mod numeric,
    found_peaks_isotopic numeric,
    flag_peak_number_exp_10 varchar(3),
    cosine_similarity_10 numeric,
    scholle_similarity_10 numeric,
    Validation text,
    acquisition_mode text,
    prob numeric,
    class numeric,
    prob_no_rt numeric,
    class_no_rt numeric,
    CONSTRAINT scores_pkey PRIMARY KEY (id_mzml, id_molecule, id_analysis, retention_time_exp)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.scores
    OWNER to "ineris";
"""

QUERY_TABLE_VALIDATION = """
-- Table: public.mzml_files
-- DROP TABLE public.validation;
CREATE TABLE public.validation 
(
    id_mzml integer NOT NULL,
    id_molecule integer NOT NULL,
    id_analysis integer NOT NULL,
    retention_time_exp numeric NOT NULL,
    validation text,
    CONSTRAINT validaiton_pkey PRIMARY KEY (id_mzml, id_molecule, id_analysis, retention_time_exp)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE public.validation
    OWNER to "ineris";
"""

QUERIES = [QUERY_TABLE_MZML_FILES, QUERY_TABLE_MOLECULES, QUERY_TABLE_ANALYSIS, QUERY_TABLE_MZML_CHROMATO, QUERY_TABLE_SEARCH_MASS_MZML, 
           QUERY_TABLE_EXTRACTED_PEAKS, QUERY_TABLE_ISOTOPIC_PROFILE, QUERY_TABLE_FRAGMENT]


if __name__ == "__main__":
    run_query(QUERY_TABLE_SCORES)