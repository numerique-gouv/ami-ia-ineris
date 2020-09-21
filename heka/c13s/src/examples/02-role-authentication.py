"""Authentication level features."""
# Import flask-related tools in order to manipulate requests and whatsoever
# Here, all the blueprints are automatically imported inside the Sialab,
# which means that in order to expose an endpoint, one simply needs to put it
# inside a blueprint in endpoint files.
from flask import jsonify, Blueprint

# In order to require authentication for an endpoint, we need to import the jwt
# Sialab extentension. This object contains the "requires_roles" decorator,
# used to add authentication to an endpoint.
from c13s.extensions import jwt

import pandas as pd


example02_bp = Blueprint("example02", __name__)


@example02_bp.route("/examples/require_role1", methods=["GET"])
@jwt.requires_roles(["Role1"])
def simple_with_role1():
    """
    Get a simple JSON.

    This endpoint requires the role "Role1".

    ---
    get:
      description: Get a simple python dict in the form of a JSON
      summary: Get a simple JSON.
      tags:
        - Authentication Examples
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
    df = pd.DataFrame(
        {
            "name": ["Nicolas", "My-An"],
            "age": ["28", "25"],
            "language": ["Python", "R"],
        }
    )

    return jsonify(df.to_dict())


@example02_bp.route("/examples/require_role2", methods=["GET"])
@jwt.requires_roles(["Role2"])
def simple_with_role2():
    """
    Get a simple JSON.

    This endpoint requires the role "Role2".

    ---
    get:
      description: Get a simple python dict in the form of a JSON
      summary: Get a simple JSON.
      tags:
        - Authentication Examples
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
    df = pd.DataFrame(
        {
            "name": ["Nicolas", "My-An"],
            "age": ["28", "25"],
            "language": ["Python", "R"],
        }
    )

    return jsonify(df.to_dict())


@example02_bp.route("/examples/require_admin", methods=["GET"])
@jwt.requires_roles(["Admin"])
def simple_with_admin():
    """
    Get a simple JSON.

    This endpoint requires the role "Admin".

    ---
    get:
      description: Get a simple python dict in the form of a JSON
      summary: Get a simple JSON.
      tags:
        - Authentication Examples
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
    df = pd.DataFrame(
        {
            "name": ["Nicolas", "My-An"],
            "age": ["28", "25"],
            "language": ["Python", "R"],
        }
    )

    return jsonify(df.to_dict())
