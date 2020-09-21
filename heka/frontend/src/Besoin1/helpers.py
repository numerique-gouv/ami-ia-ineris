from google.cloud import storage
from google.oauth2.service_account import Credentials
import pymzml
import re
import yaml
import json
import os
import psycopg2
import pandas as pd
import pandas.io.sql as sqlio


cfg = json.loads(os.environ["PROVIDER_CREDENTIALS"])
FILE_PATH_BASE = '/heka/storage/'


def get_compo(str):
    element_pat = re.compile("([A-Z][a-z]?)(\d*)")
    all_elements = {}
    for (element_name, count) in element_pat.findall(str):
        if count == "":
            count = 1
        else:
            count = int(count)
        all_elements[element_name]=count
    return(all_elements)



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



def get_colision_energy(spec):
    if spec['collision energy'] == None:
        return(0)
    return(spec['collision energy'])


def get_mzml_values(path):
    mzml_file = FILE_PATH_BASE + path
    run = pymzml.run.Reader(mzml_file)
    L=[]
    for n, spec in enumerate(run):
        L.append(f"spectrum {spec.ID} at RT {round(spec.scan_time_in_minutes(),2)} min and collision energy of {get_colision_energy(spec)} eV")
    return(L)



def _storage_client():
    """retuns the client creds to be used while accessing bucket"""
    credentials = Credentials.from_service_account_info(
        cfg
    )
    client = storage.Client(
        project=credentials.project_id, credentials=credentials
    )
    return client


def _bucket_name():
    credentials = Credentials.from_service_account_info(
        cfg
    )
    env = credentials.project_id.split("-")[-1]
    prefix = credentials.project_id.split("-")[0]
    project_name = credentials.service_account_email.split("@")[0].replace(
        f"{prefix}-", ""
    )
    return f"{prefix}-{env}-{project_name}-storage"





def list_blobs():
    """Lists all the blobs in the bucket"""
    storage_client = _storage_client()
    bucket_name = _bucket_name()
    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs()
    return [
        {
            "blob_name": blob.name,
            "size": blob.size,
            "updated": blob.updated,
            "md5_hash": blob.md5_hash,
        }
        for blob in blobs
    ]
