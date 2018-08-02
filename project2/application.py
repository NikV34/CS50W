import os
from flask import Flask, session, request
from flask_socketio import SocketIO, emit
from flask import render_template, redirect, url_for

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")
socketio = SocketIO(app)


@app.route("/", methods=['GET', 'POST'])
def index():
    if 'username' in session:
        logIn = True
        print(session['username'])
    else:
        if request.method == 'GET':
            return render_template('enter_name.html')
        else:
            session['username'] = request.form['username']


if __name__ == '__main__':
    app.env = 'development'
    app.debug = True
    #app.secret_key = os.environ.get('SECRET_KEY', 'dev')
    app.run()