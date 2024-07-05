# flask_sqlalchemy_db_of_books
Welcome to my project page!
## Introduction
This is an exercise in building a webpage representation of and an interface for a books database CRUD

### Tags
`Flask-SQLAlchemy` `html` `css` `python` `flask` `SSR` `microframework` `Jinja2` `API fetching`

### Project features
* SQLite db management
* endpoint routing
* image fetching from an API
* templating / dynamic webpage generation via Jinja2
* constraints flow design


## Installation

To install this project, clone the repository and install the dependencies listed in requirements.txt. If on Windows, rely on `pip` rather than pip3.

```bash
  pip3 install -r requirements.txt
```

## Usage/Examples

> [!NOTE]
> The home endpoint `/` loads slowly. This is by design, because the project requirements didn't allow permanent storage of the image URLs in the database.

### Instructions

Run app.py either from your IDE or from the terminal.

```bash
python3 app.py
```

Interact with the webpage via a browser of your choice at
```
http://127.0.0.1:5000/
```
i.e.
```
http://localhost:5000/
```

If you wish to start your own database from scratch,
1. delete the file `data/library.sqlite`
2. uncomment (Ctrl+/) the following in app.py:
```python
with app.app_context():
    try:
        db.create_all()
        print("Tables created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
```

### Demo screenshot:

#### Homepage
![image](https://github.com/MilosTadic01/flask_sqlalchemy_db_of_books/assets/140609365/ed8b8ca9-b72d-43cc-b1f0-a5f6ca2a4d35)

#### Adding a book
ISBN input is mandatory to ensure success in fetching an appropriate image from [OpenLibrary's API](https://openlibrary.org/developers/api). The formatting shouldn't matter, feel free to omit the hyphens or use ISBN10 as equal to ISBN13.
![image](https://github.com/MilosTadic01/flask_sqlalchemy_db_of_books/assets/140609365/11e35f0a-dfef-4417-8fe9-241fc1bc1c21)


## Feedback

If you have any feedback, please reach out to me @MilosTadic01


## License

[CC0 1.0 Universal](https://choosealicense.com/licenses/cc0-1.0/)

