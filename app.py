import os
import requests
from datetime import datetime
from werkzeug.exceptions import BadRequest
from flask import Flask, request, abort, jsonify, render_template
from data_models import db, Author, Book

GET_COVER_PREF = "https://covers.openlibrary.org/b/isbn/"
GET_COVER_SUFF = "-M.jpg"

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


@app.route('/')
def index():
    """Render a page with database contents + book cover images. I don't
    understand why we couldn't only fetch the cover image urls once and store
    them in the DB, this is making the "rendering" much longer.

    db.session.query allows column specs; returns [tuples]
    Model.query (Book.query) forbids columns specs; returns [ORM objects] """
    rows = db.session.query(Book.title, Book.author_id, Book.isbn).all()
    sort_crit = request.args.get('sort')
    sort_dir = request.args.get('dir')
    if sort_crit:
        rows = get_sorted_rows(sort_crit, sort_dir)
    # Prepare a list of dicts to pass to Jinja2 in the html to render
    books_list = []
    for row in rows:
        # automatically finds the existing db.session, no need to specify
        author_entry = Author.query.filter(Author.author_id == row[1]).one()
        author_name = "by <blank>"
        if author_entry:
            author_name = author_entry.name
        cover_url = fetch_cover_url(row[2])
        books_list.append(
            {'title': row[0],
             'author': author_name,
             'cover_url': cover_url}
        )
    return render_template('home.html', books=books_list), 200


def get_sorted_rows(sort_crit, sort_dir):
    """Handle sorting args in the query string."""
    if sort_crit == 'title':
        if sort_dir == 'desc':
            rows = db.session.query(Book.title, Book.author_id, Book.isbn) \
                .order_by(Book.title.desc()).all()
        else:
            rows = db.session.query(Book.title, Book.author_id, Book.isbn) \
                .order_by(Book.title).all()
    elif sort_crit == 'author':
        if sort_dir == 'desc':
            rows = db.session.query(Book.title, Book.author_id, Book.isbn) \
                .join(Author).order_by(Author.name.desc()).all()
        else:
            rows = db.session.query(Book.title, Book.author_id, Book.isbn) \
                .join(Author).order_by(Author.name).all()
    else:  # for 'year'
        if sort_dir == 'desc':
            rows = db.session.query(Book.title, Book.author_id, Book.isbn) \
                .order_by(Book.year.desc()).all()
        else:
            rows = db.session.query(Book.title, Book.author_id, Book.isbn) \
                .order_by(Book.year).all()
    return rows


@app.route('/search')
def search():
    """Returns a list of books where search query matches at least one of
    ["title", "author", "publication_year"]. Year as string, so 199 works."""
    search_term = request.args.get('search').lower()
    rows = db.session.query(Book.title, Book.author_id, Book.isbn,
                            Book.publication_year).all()
    books_list = []
    for row in rows:
        author_entry = Author.query.filter(Author.author_id == row[1]).one()
        author_name = "by <blank>"
        if author_entry:
            author_name = author_entry.name
        if search_term not in row[0].lower() \
                and search_term not in str(row[3]).lower() \
                and search_term not in author_name.lower():
            continue
        cover_url = fetch_cover_url(row[2])
        books_list.append(
            {'title': row[0],
             'author': author_name,
             'cover_url': cover_url}
        )
    return render_template('home.html', books=books_list), 200


def fetch_cover_url(isbn):
    """Fetch an image from OpenLibrary API. If unsuccessful facilitate for the
    displaying of alt= in the html."""
    cover_url = requests.get(GET_COVER_PREF + isbn + GET_COVER_SUFF).url
    if not cover_url:
        cover_url = ""
    return cover_url


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """Add author entry to authors table. MIME type remarks:
    We are NOT in fact expecting JSON as Content-Type (application/json),
    bc we have no JS or cURL or Postman to set that up in the body. Instead,
    we are working with the default application/x-www-form-urlencoded, meaning
    we should use request.form.get() rather than request.get_json()."""
    if request.method == 'GET':
        return render_template('add_author.html')
    elif request.method == 'POST':
        name = request.form.get('name')
        birth = request.form.get('birthdate')
        death = request.form.get('date_of_death')
        if not name or not birth:  # redundant with html 'required', but still
            abort(400)
        new_author = Author()  # w/o attr 1st, so that I can check if 'death'
        new_author.name = name
        # Convert html date to Py datetime object, Flask-SQLAlchemy wants it
        new_author.birth_date = datetime.strptime(birth, '%Y-%m-%d')
        if death:
            new_author.date_of_death = datetime.strptime(death, '%Y-%m-%d')
        db.session.add(new_author)
        db.session.commit()
        return jsonify(message=f"Author {request.form.get('name')} "
                       "added to database."), 201


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """Add book entry to books table. Display dropdown menu to force
    author input first."""
    if request.method == 'GET':
        authors_dict = {}

        # Previously with sqlalchemy:
        # results = connection.execute(text(QUERY))
        # rows = results.fetchall()

        # With Flask-SQLAlchemy you don't even need the QUERY
        rows = db.session.query(Author.name, Author.author_id).all()
        for row in rows:
            authors_dict.update({row[0]: row[1]})
        return render_template('add_book.html',
                               authors_dict=authors_dict)
    elif request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        pub_year = request.form.get('pub_year')
        author_id = request.form.get('author')
        if not (title and isbn and pub_year and author_id):
            abort(400)
        new_book = Book(
            title=title,
            isbn=isbn,
            publication_year=pub_year,
            author_id=author_id
        )
        db.session.add(new_book)
        db.session.commit()
        return jsonify(message=f"'{title}' added to database."), 201


@app.errorhandler(400)
def error_bad_request(error):
    """Handles bad sorting params for 'GET' and missing info for 'POST'."""
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
