import os
from datetime import datetime
from werkzeug.exceptions import BadRequest
from flask import Flask, request, abort, jsonify, render_template
from data_models import db, Author, Book

AUTHOR_ENTRY_COMPONENTS = ["name", "birthdate", "date_of_death"]
BOOK_ENTRY_COMPONENTS = ["title", "isbn", "publication_year", "author"]


app = Flask(__name__)
# instead of 'engine = create_engine('sqlite:///data/restaurants.sqlite')':
db_path = os.path.join(os.getcwd(), 'data', 'library.sqlite')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
db.init_app(app)

# Create tables, feel free to comment out after running once, though no need
# with app.app_context():
#     try:
#         db.create_all()
#         print("Tables created successfully.")
#     except Exception as e:
#         print(f"Error creating tables: {e}")


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """We are NOT in fact expecting JSON as Content-Type (application/json),
    bc we have no JS or cURL or Postman to set that up in the body. Instead,
    we are working with the default application/x-www-form-urlencoded, meaning
    we should use request.form.get() rather than request.get_json()."""
    if request.method == 'GET':
        return render_template('add_author.html')
    elif request.method == 'POST':
        name = request.form.get('name')
        birth = request.form.get('birthdate')
        death = request.form.get('date_of_death')
        if not name or not birth:
            abort(400)
        new_author = Author()
        new_author.name = name
        # Convert html date to Py datetime object, sqlalchemy wants it
        new_author.birth_date = datetime.strptime(birth, '%Y-%m-%d')
        if death:
            new_author.date_of_death = datetime.strptime(death, '%Y-%m-%d')
        db.session.add(new_author)
        db.session.commit()
        return jsonify(message=f"Author {request.form.get('name')} "
                       "added to database."), 201


@app.errorhandler(400)
def error_bad_request(error):
    """Handles bad sorting params for 'GET', missing info for 'POST'
    and bad keys for 'PUT'."""
    if request.method == 'GET':
        pass
    else:  # for 'POST' and 'PUT'
        return jsonify(message="Error: No fields may be empty"), 400


@app.errorhandler(404)
def error_not_found(error):
    """Return json informing user the endpoint was not found & 404."""
    err_msg = f"{request.path} Not Found"
    return jsonify(message=f"Error 404: {err_msg}"), 404


if __name__ == '__main__':
    app.run(debug=True)
