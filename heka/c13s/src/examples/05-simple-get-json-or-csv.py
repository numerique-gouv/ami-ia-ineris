"""Simple Sialab features."""
# Import flask-related tools in order to manipulate requests and whatsoever
# Here, all the blueprints are automatically imported inside the Sialab,
# which means that in order to expose an endpoint, one simply needs to put it
# inside a blueprint in endpoint files.
from flask import jsonify, send_file, Blueprint

# io and pandas are libraries used by the code inside te endpoints.
from io import BytesIO
import pandas as pd

from flask_csv import send_csv

# An endpoint corresponds to a function (which reutrns the endpoint's response)
# and is decorated with @blueprint.route. Inside we can do whatever we want and
# return the results.
# In order to have the endpoint listed inside the API specification (OpenAPI3),
# the user needs insert valid YAML specification inside the docstring of
# the given function. This specification can be found in here :
# https://swagger.io/docs/specification/paths-and-operations/#operations
#
# !IMPORTANT: the functions names cannot be the same, *accross all the code*

example05_bp = Blueprint("example05", __name__)

@example05_bp.route("/examples/simple_json_or_csv", methods=["GET"])
def simple_get_json_or_csv():
    """
    Get a simple JSON or CSV based on query param 'format'.

    ---
    get:
      description: Get a simple python dict in the form of a JSON or CSV.
      summary: Get a simple JSON or CSV.
      tags:
        - JSON or CSV Examples
      parameters:
        - in: query
          name: format
          required: false
          schema:
            type: string
            enum: [json, csv]
      responses:
        200:
          description: simple data
          content:
            application/json:
              schema:
                type: string
            text/csv:
              schema:
                type: string
    """

    return jsonify([
        {
            "name": "Nicolas",
            "age": "28",
            "language": "Python"
        },
        {
            "name": "My-An",
            "age": "25",
            "language": "R"
        }
    ])
