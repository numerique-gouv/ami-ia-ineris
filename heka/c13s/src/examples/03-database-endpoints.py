"""Database read features."""
# Import flask-related tools in order to manipulate requests and whatsoever
# Here, all the blueprints are automatically imported inside the Sialab,
# which means that in order to expose an endpoint, one simply needs to put it
# inside a blueprint in endpoint files.
from flask import jsonify, Blueprint

# In order to directly interact with the database, we need to import the
# SQLAlchemy object "db".
from c13s.extensions import db

from datetime import datetime

example03_bp = Blueprint("example03", __name__)


@example03_bp.route("/examples/role_read_many", methods=["GET"])
def database_read_many():
    """
    Select information from the database.

    ---
    get:
      description: Select information from an internal table in the database
      summary: Select information from the database.
      tags:
        - Database Examples
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
    # SQL Query to execute
    query = "SELECT * FROM heka_backend.roles;"

    # Execute it through the db.engine.execute method.
    # The ResultProxy object ("db.engine.execute(req)") contains several
    # different methods. More information can be found on the link below
    # [https://docs.sqlalchemy.org/en/13/core/connections.html?highlight=fetcha
    # ll#sqlalchemy.engine.ResultProxy]
    result = db.engine.execute(query).fetchall()

    return jsonify([dict(row) for row in result])


@example03_bp.route("/examples/role_read_one", methods=["GET"])
def database_read_one():
    """
    Select information from the database.

    ---
    get:
      description: Select information from an internal table in the database
      summary: Select information from the database.
      tags:
        - Database Examples
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
    # SQL Query to execute
    query = "SELECT * FROM heka_backend.roles;"

    result = db.engine.execute(query).fetchone()

    return jsonify(dict(result))


# It is recommended to use the POST method to modify data on the database,
# PUT to insert new data and DELETE to remove data.


@example03_bp.route("/examples/role_write_many", methods=["POST"])
def database_write_many():
    """
    Select information from the database.

    ---
    get:
      description: Select information from an internal table in the database
      summary: Select information from the database.
      tags:
        - Database Examples
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
    # SQL Query to execute
    query = (
        "INSERT INTO heka_backend.roles (description, name) "
        "VALUES ('Test Insertion','Test {}') RETURNING id;".format(
            datetime.now()
        )
    )

    # Execute it through the db.engine.execute method.
    # The ResultProxy object ("db.engine.execute(req)") contains several
    # different methods. More information can be found on the link below
    # [https://docs.sqlalchemy.org/en/13/core/connections.html?highlight=fetcha
    # ll#sqlalchemy.engine.ResultProxy]
    result = db.engine.execute(query).fetchone()

    db.session.commit()

    return jsonify(dict(result))
