import os
import json
import requests
from flask import request
from flask import Flask, session
from flask import render_template, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)


# Check for environment variable
os.environ["DATABASE_URL"] = 'postgres://nhedgifrbqclmi:9d969bc86ee5bcb1ddbe7ffa81ad51003003fa99ae916a4ded2fd2486db2db1b@ec2-54-217-205-90.eu-west-1.compute.amazonaws.com:5432/d31etsp4aep187'
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))




@app.route("/")
def index():
    if 'username' in session:
        logIn = True
    else:
        logIn = False
    # res = requests.get("https://www.goodreads.com/book/review_counts.json",
    #                    params={"key": "5ccG1d3jk4MQbymFZ4LsdQ", "isbns": "9781632168146"})
    # print(res.json())
    # return str(res.json())
    return render_template('index.html', logIn=logIn)


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    if 'username' in session:
        logIn = True
    else:
        logIn = False
    #print(request)
    #print(request.form)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        userInfo = engine.execute(f"select * from users where username = '{username}';").first()
        if userInfo or not username or not password:
            return render_template('registration.html', error="INVALID USERNAME OR PASSWORD", logIn=logIn)
        else:
            if not userInfo and username and password:
                engine.execute(f"insert into users (username,password) values ('{username}','{generate_password_hash(password)}');")
                #session['username'] = username
        return redirect(url_for('index'))
    else:
        return render_template('registration.html', error="We'll never share your username with anyone else", logIn=logIn)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        userInfo = engine.execute(f"select * from users where username = '{username}';").first()
        if not userInfo or not username or not password or check_password_hash(password, generate_password_hash(userInfo.password)):
            return render_template('login.html', error="INVALID USERNAME OR PASSWORD", logIn=False)
        else:
            if userInfo and username and password:
                session['username'] = username
                #print(userInfo.username)

        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        if 'username' in session:
            logIn = True
            return render_template('search.html', logIn=logIn)
        else:
            return redirect(url_for('index'))
    if request.method == 'POST':
        if 'username' in session:
            logIn = True
        query = request.form['query']
        if not query:
            resultTitle = "No books"
            result = ""
        else:
            resultTitle = "Search books results"
            result = engine.execute(f"select * from books where concat(isbn,title,author) like '%%{query}%%';").fetchall()
        return render_template('search_results.html', resultTitle=resultTitle, logIn=logIn, result=result)


@app.route('/book/<isbn>', methods=['GET', 'POST'])
def book(isbn):
    book = engine.execute(f"select * from books where isbn='{isbn}';").first()
    if 'username' in session:
        user_id = engine.execute(f"select * from users where username = '{session['username']}';").first()
        visibleReview = engine.execute(f"select * from reviews where user_id={user_id.id} and book_id={book.id};").first()
        #print(visibleReview)
        if request.method == 'POST':
            # print('book_id', book.id)
            # print('username', session['username'])
            # print(request.form)
            engine.execute(
                f"insert into reviews (book_id,user_id,rating,review) values ('{book.id}','{user_id.id}','{request.form['rating']}','{request.form['review']}');")
            visibleReview = True
        logIn = True
        try:
            res = requests.get("https://www.goodreads.com/book/review_counts.json",
                               params={"key": "5ccG1d3jk4MQbymFZ4LsdQ", "isbns": book.isbn}).json()
            average_rating = res['books'][0]['average_rating']
            ratings_count = res['books'][0]['ratings_count']
        except:
            average_rating = "No average rating"
            ratings_count = "No ratings count"
        allReviews = engine.execute(f"select * from reviews where book_id={book.id};").fetchall()
        return render_template('book.html', logIn=logIn, book=book, average_rating=average_rating,
                               ratings_count=ratings_count, visibleReview=visibleReview, allReviews=allReviews)
    else:
        return redirect(url_for('index'))


@app.route('/api/<isbn>', methods=['GET'])
def api(isbn):
    book = engine.execute(f"select * from books where isbn='{isbn}';").first()
    try:
        res = requests.get("https://www.goodreads.com/book/review_counts.json",
                           params={"key": "5ccG1d3jk4MQbymFZ4LsdQ", "isbns": book.isbn}).json()
        average_rating = res['books'][0]['average_rating']
        ratings_count = res['books'][0]['ratings_count']
    except:
        average_rating = "No average rating"
        ratings_count = "No ratings count"
    return (json.dumps({"book": {
                    "title": book.title,
                    "author": book.author,
                    "year": book.year,
                    "isbn": isbn,
                    "review_count": ratings_count,
                    "average_score": average_rating
                     }}))



if __name__ == '__main__':
    app.env = 'development'
    app.debug = True
    app.secret_key = os.environ.get('SECRET_KEY', 'dev')
    app.run()