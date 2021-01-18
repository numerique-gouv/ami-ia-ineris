from flask import jsonify, send_file, Blueprint, Response
from io import BytesIO
import pandas as pd
import yaml
import psycopg2
import pandas.io.sql as sqlio
import os
from datetime import date

blueprint = Blueprint("get_db", __name__)

@blueprint.route("/get_db", methods=["GET"])
def get_db():
    """
    Get a simple JSON or CSV based on query param 'format'.

    ---
    get:
      description: Get a simple python dict in the form of a JSON or CSV.
      summary: Get a simple JSON or CSV.
      tags:
        - Database
      parameters:
        - in: query
          name: format
          required: false
          schema:
            type: string
            enum: [csv, json]
      responses:
        200:
          description: simple data
          content:
            text/csv:
              schema:
                type: string
            application/json:
              schema:
                type: string
    """

    substances = ['2378-TCDD', '12378-PeCDD', '123478-HxCDD', '123678-HxCDD',
      '123789-HxCDD', '1234678-HpCDD', 'OCDD', '2378-TCDF', '12378-PeCDF',
      '23478-PeCDF', '123478-HxCDF', '123678-HxCDF', '234678-HxCDF',
      '123789-HxCDF', '1234678-HpCDF', '1234789-HpCDF', 'OCDF']

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
    query = """
        SELECT "Fournisseur", "Nom_du_projet", "Catégorie_de_l'activité_industrielle", "Sous-catégorie", "Réf._échantillon", "Réf._Synthese", "Coord._Lat._Source", "Coord._Long._Source", "Localisation_de_la_source", "Coord._Lat._Point", "Coord._Long._Point", "Distance_à_la_source_km", "Précisions_sur_l'emplacement", "Type_de_point_de_mesure", "Fiabilité_donnée_de_l'emplacement", "Complément", "Date_de_mesure_:__Début", "Date_de_mesure_:__Fin", "Année", "Date_de_l'accident", "Délai_min._d'intervention_jours", "Délai_max._d'intervention_jours", "Source", "Contexte", "Matrice", "Direction_des_vents_dominants", "Direction_des_vents_secondaires", "Force_des_vents__m/s", "Pluviométrie_mm/min", "Température_C", "Humidité_Relative_", "Gestion_Limite_Analytique", "Unités", "Somme_PCDD", "2378-TCDD", "<", "12378-PeCDD", "<.1", "123478-HxCDD", "<.2", "123678-HxCDD", "<.3", "123789-HxCDD", "<.4", "1234678-HpCDD", "<.5", "OCDD", "<.6", "Somme_PCDF", "2378-TCDF", "<.7", "12378-PeCDF", "<.8", "23478-PeCDF", "<.9", "123478-HxCDF", "<.10", "123678-HxCDF", "<.11", "234678-HxCDF", "<.12", "123789-HxCDF", "<.13", "1234678-HpCDF", "<.14", "1234789-HpCDF", "<.15", "OCDF", "<.16", "Somme_PCDD-PCDF", "Total_TCDD", "<.17", "Total_PeCDD", "<.18", "Total_HxCDD", "<.19", "Total_HpCDD", "<.20", "Total_DIOXINE", "<.21", "Total_TCDF", "<.22", "Total_PeCDF", "<.23", "Total_HxCDF", "<.24", "Total_HpCDF", "<.25", "Total_FURANE", "<.26", "Total_DIOXINE_FURANE", "Commentaire"
        FROM public.data_ineris;
    """
    df = sqlio.read_sql_query(query, conn)
    conn.close()

    today = date.today()
    name = "data_platform_" + today.strftime("%Y%m%d")

    return Response(
        df.to_csv(index=False, encoding="utf-8", sep=";"),
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=" + name + ".csv"})
