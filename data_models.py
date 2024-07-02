from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Author(db.Model):
    """Author table, ORM style."""
    __tablename__ = 'authors'

    author_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date)

    def __str__(self):
        return f"{self.name}, born {self.birth_date}"

    def __repr__(self):
        return f"Author(id: {self.author_id}, name: {self.name})"


class Book(db.Model):
    """Book table, ORM style."""
    __tablename__ = 'books'

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(17), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    publication_year = db.Column(db.SmallInteger, nullable=False)
    # ForeignKey must match the __tablename__ attr. of Parent
    author_id = db.Column(db.Integer, db.ForeignKey('authors.author_id'),
                          nullable=False)

    # Define the relationship to the Parent model
    # this also automatically adds a 'books' attribute to the Parent
    author = db.relationship('Author', backref=db.backref('books',
                             lazy=True))

    def __str__(self):
        return f"{self.title} by {self.author_id}, {self.publication_year}"

    def __repr__(self):
        return f"Book(id: {self.id}, title: {self.title}, isbn: {self.isbn})"
