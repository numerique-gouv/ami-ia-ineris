"""Simple Sialab features."""
# Import flask-related tools in order to manipulate requests and whatsoever
# Here, all the blueprints are automatically imported inside the Sialab,
# which means that in order to expose an endpoint, one simply needs to put it
# inside a blueprint in endpoint files.
from flask import jsonify, send_file, Blueprint

# io and pandas are libraries used by the code inside te endpoints.
from io import BytesIO
import pandas as pd

# An endpoint corresponds to a function (which reutrns the endpoint's response)
# and is decorated with @blueprint.route. Inside we can do whatever we want and
# return the results.
# In order to have the endpoint listed inside the API specification (OpenAPI3),
# the user needs insert valid YAML specification inside the docstring of
# the given function. This specification can be found in here :
# https://swagger.io/docs/specification/paths-and-operations/#operations
#
# !IMPORTANT: the functions names cannot be the same, *accross all the code*

example01_bp = Blueprint("example01", __name__)


@example01_bp.route("/examples/simple_json", methods=["GET"])
def simple_get_json():
    """
    Get a simple JSON.

    ---
    get:
      description: Get a simple python dict in the form of a JSON
      summary: Get a simple JSON.
      tags:
        - Simple Examples
      responses:
        200:
          description: A simple json
          content:
            application/json:
              schema:
                type: object
                properties:
                  name:
                    type: string
                  age:
                    type: number
                  language:
                    type: number
    """
    # Inside the function, we can write whatever code we want
    df = pd.DataFrame(
        {
            "name": ["Nicolas", "My-An"],
            "age": ["28", "25"],
            "language": ["Python", "R"],
        }
    )

    # The return value is what is the response behind the request. It needs to
    # be jsonified before being sent.
    return jsonify(df.to_dict())
