"""Database read features."""
from flask import request, jsonify, Blueprint

from c13s.extensions import db, ma

example04_bp = Blueprint("example04", __name__)

# In order to simplify and organize interactions with the database, one can use
# a ORM (Object Relationship Manager).This project uses SQL Alchemy as an ORM
# and Marshmallow as an object serializer.


# Here is how one can build an Object Class with the ORM.
class Book(db.Model):
    """
    Book class.

    This class serves as an example on how to use the ORM.
    """

    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    description = db.Column(db.String(200))

    def __init__(self, name, description):
        """Construct the Book instances."""
        self.name = name
        self.description = description


# Once the class is built, the serializer is needed in order to be able to send
# it through API requests. This is done by creating a Marshmallow scheme.


class BookSchema(ma.ModelSchema):
    """
    Book Schema.

    This class serves as an example on how to use the Serializer.
    """

    class Meta:
        """Model definition for RoleSchema."""

        model = Book


book_schema = BookSchema()
books_schema = BookSchema(many=True)

# Finally, The serializer and Object Class can be used to serve data in an
# endpoint.


@example04_bp.route("/books/create_table", methods=["PUT"])
def create_table_books():
    """
    Create the table for book objects.

    ---
    put:
      description: Creates the table for book objects.
      summary: Creates the table for book objects.
      tags:
        - ORM Examples
      responses:
        200:
          description: Status of the request
          content:
            application/json:
              schema:
                type: object
    """

    db.create_all()

    return jsonify({"result": "OK"})


@example04_bp.route("/books", methods=["GET"])
def get_books():
    """
    Get all Books.

    ---
    get:
      description: Get all Books
      summary: Get all Books
      tags:
        - ORM Examples
      responses:
        200:
          description: All books
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
    """

    all_books = Book.query.all()
    result = books_schema.dump(all_books)

    return jsonify(result.data)


@example04_bp.route("/books", methods=["PUT"])
def put_books():
    """
    Put a Book.

    ---
    put:
      description: Insert a Book
      summary: Insert a Book
      tags:
        - ORM Examples
      requestBody:
        content:
          application/json:
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
                description:
                  type: string
      responses:
        201:
          description: The added object
          content:
            application/json:
              schema:
                type: object
    """
    name = request.json["name"]
    description = request.json["description"]

    new_book = Book(name, description)
    db.session.add(new_book)
    db.session.commit()

    return book_schema.jsonify(new_book), 201


@example04_bp.route("/books/<book_id>", methods=["POST"])
def post_books(book_id):
    """
    Modify a given book.

    ---
    post:
      description: Modify a given book
      summary: Modify a given book
      tags:
        - ORM Examples
      requestBody:
        content:
          application/json:
            required: true
            schema:
              type: object
              properties:
                name:
                  type: string
                description:
                  type: string
      parameters:
        - name: book_id
          in: path
          schema:
            type: number
          required: true
          description: The Books's id
      responses:
        200:
          description: The modified object.
          content:
            application/json:
              schema:
                type: object
    """
    book = Book.query.get(book_id)

    if "name" in request.json:
        book.name = request.json["name"]
    if "description" in request.json:
        book.description = request.json["description"]

    db.session.commit()

    return book_schema.jsonify(book)


@example04_bp.route("/books/<book_id>", methods=["DELETE"])
def delete_books(book_id):
    """
    Delete a given book.

    ---
    delete:
      description: Delete a given book.
      summary: Delete a given book.
      tags:
        - ORM Examples
      parameters:
        - name: book_id
          in: path
          schema:
            type: number
          required: true
          description: The Books's id
      responses:
        200:
          description: The deleted object.
          content:
            application/json:
              schema:
                type: object
    """
    book = Book.query.get(book_id)
    db.session.delete(book)
    db.session.commit()

    return book_schema.jsonify(book)
