import os
import datetime
import requests

#8WlLqUYMtkRokvOkYOsVT4pY7joahAZM

# http://openlibrary.org/search.json?q=the+lord+of+the+rings
# http://openlibrary.org/search.json?title=the+lord+of+the+rings
# http://openlibrary.org/search.json?author=tolkien
# http://openlibrary.org/search.json?q=the+lord+of+the+rings&page=2
# http://openlibrary.org/search/authors.json?q=twain

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///books.db")

# Configure recommendations dictionary
RECOMMENDS = requests.get(f"https://api.nytimes.com/svc/books/v3/lists/current/hardcover-fiction.json?&api-key=8WlLqUYMtkRokvOkYOsVT4pY7joahAZM").json()
RECOMMEND_LIST = {}
# 'title': None, 'author': None, 'description': None, 'rank': None, 'book_image': None
for entry in RECOMMENDS["results"]["books"]:
    RECOMMEND_LIST[entry['title'].title()] = {'author':entry['author'], 'description':entry['description'], 'rank':entry['rank'], 'book_image':entry['book_image']}


@app.route("/", methods=["GET","POST"])
@login_required
def index():
    """Show reading list"""

    db.execute("CREATE TABLE IF NOT EXISTS list (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, user_id INTEGER NOT NULL, title TEXT NOT NULL, author TEXT NOT NULL, read BOOLEAN DEFAULT 0 NOT NULL, add_time TEXT NOT NULL, read_time TEXT DEFAULT 'unread', diff TEXT DEFAULT 'none')")

    books_list = db.execute("SELECT title, author, add_time FROM list WHERE user_id = ? AND read=0", session["user_id"])

    if request.method == "GET":
        return render_template("index.html", books_list = books_list)

    if request.method == "POST":
        books_read = request.form.getlist("book")
        time = datetime.date.today()

        for book in books_read:
            book = book.strip()

            added = db.execute("SELECT add_time FROM list WHERE user_id = ? AND title = ?", session["user_id"], book)[0]['add_time']
            d = (time - datetime.datetime.strptime(added, '%Y-%m-%d').date()).days

            db.execute("UPDATE list SET read = 1, read_time = ?, diff = ? WHERE user_id = ? AND title = ?", time, d, session["user_id"], book)

        books_list = db.execute("SELECT title, author, add_time FROM list WHERE user_id = ? AND read=0", session["user_id"])

        return render_template("index.html", books_list = books_list)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    """Add books to list"""

    if request.method == "GET":
        return render_template("add.html")

    if request.method == "POST":
        if not request.form.get("title"):
            return apology("input title")

        if not request.form.get("author"):
            return apology("input author")

        title = request.form.get("title").title()
        author = request.form.get("author").title()
        time = datetime.date.today()

        search_title = title.replace(" ", "+")
        # print(search_title)
        # book_info = requests.get(f"http://openlibrary.org/search.json?title={search_title}").json()
        # authors = []
        # for book in book_info['docs']:
        #     print(book['title'])
        # print(authors)
        # return render_template("add.html", book_info = book_info)
        # print(book_info.json()['docs'][0]['author_name'])

        db.execute("INSERT INTO list (user_id, title, author, add_time) VALUES (?, ?, ?, ?)", session["user_id"],title, author, time)
        return redirect("/")


@app.route("/read", methods=["GET", "POST"])
@login_required
def read():
    """Show list of books read"""

    if request.method == "GET":
        books_list = db.execute("SELECT title, author, read_time, add_time FROM list WHERE user_id = ? AND read=1", session["user_id"])
        return render_template("read.html", books_list = books_list)

    if request.method == "POST":
        books_unread = request.form.getlist("book")
        time = datetime.date.today()

        for book in books_unread:
            book = book.strip()
            db.execute("UPDATE list SET read = 0, add_time = ? WHERE user_id = ? AND title = ?", time, session["user_id"], book)

        books_list = db.execute("SELECT title, author, read_time, add_time FROM list WHERE user_id = ? AND read=1", session["user_id"])
        # [{'title': 'Jane Eyre', 'author': 'Charlotte Bronte', 'read_time': '2021-12-26'}]
        # d = datetime.datetime.strptime(s, '%m/%d/%Y')

        return render_template("read.html", books_list = books_list)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # REGISTER USER

    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 400)

        elif not request.form.get("password"):
            return apology("must provide password", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username is unique
        if len(rows) > 0:
            return apology("username already taken", 400)

        pwd = request.form.get("password")

        # Ensure passwords match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)

        # Make hash for password
        pwd = generate_password_hash(request.form.get("password"))

        # Add information into SQL
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get("username"), pwd)
        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/recommend", methods=["GET", "POST"])
@login_required
def recommend():

    if request.method == "GET":
        return render_template("recommend.html", recs=RECOMMEND_LIST)

    if request.method == "POST":
        books_unread = request.form.getlist("book")
        print(f"SLKDFJLSDJLSJF {books_unread}")
        time = datetime.date.today()

        for book in books_unread:
            print(RECOMMEND_LIST[book]['author'])
            db.execute("REPLACE INTO list (title, author, add_time, read, user_id) VALUES (?, ?, ?, ?, ?)",  book, RECOMMEND_LIST[book]['author'], time, 0, session['user_id'])
            # db.execute("INSERT INTO list (title, author, add_time) VALUES (?, ?, ?) ON CONFLICT(?) DO UPDATE SET read=0 WHERE user_id = ?", book, RECOMMEND_LIST[book]['author'], time, book, session['user_id'])
            # db.execute("INSERT INTO list (title, author, add_time) VALUES (?, ?, ?) ON DUPLICATE KEY UPDATE read=0",book, RECOMMEND_LIST[book]['author'], time)
            # db.execute("UPDATE list SET read = 0 WHERE user_id = ? AND title = ?", session["user_id"], book)

        # [{'title': 'Jane Eyre', 'author': 'Charlotte Bronte', 'read_time': '2021-12-26'}]
        # d = datetime.datetime.strptime(s, '%m/%d/%Y')

        return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
