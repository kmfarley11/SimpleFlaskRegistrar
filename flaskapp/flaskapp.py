#######################################################################################
# flaskapp.py
#   houses the main web server code for assignment #1
#   urls = 
#       '/'         : the sign in page (enter a username & password)
#       '/register' : if a new username was entered from '/', prompts for more info
#       '/viewdb'   : post register/signin with a stored username displays user info
#
#   Note: the html has not been cleaned much and inputs need sanitization
#       but it does effectively allow new users to register and displays stored users if authenticated
#######################################################################################

from collections import Counter
import bcrypt
from flask import Flask, request, g, render_template, flash, redirect, url_for, session
import os
import sqlite3
#from flask_login import LoginManager

app = Flask(__name__)

# TODO: move config to separate file...
if __name__ != '__main__':
    APP_PATH = os.path.abspath(os.path.dirname(__file__)) #'/home/ubuntu/flaskapp'
    DATABASE = APP_PATH + '/flaskapp.db'
    SALT_PATH = APP_PATH + '/salt.txt'
    SALT = ''
    with open(SALT_PATH, 'r') as sp:
        SALT = sp.read()
    SECRET_KEY = 'super secret key'
    DEBUG = True
    SESSION_TYPE = 'filesystem'
    app.config.from_object(__name__)


# TODO: use login manager... (need to fix mod_wsgi/venv for that though...)
#login_manager = LoginManager()


# check session for username and hashed password, verify in the db
# returns True if valid, False if new user, raises exception if invalid
def authenticate():
    if not session['username'] or not session['hashed']:
        raise Exception('ERROR: username/hash not provided!?')
    uname = session['username']
    usrget = execute_query('SELECT password FROM flaskapp WHERE username=?', (uname,))
    hashed = session['hashed']
    if usrget:
        if hashed == usrget[0][0]:
            return True
        else:
            raise Exception('Incorrect password for "%s"' % (uname))
    return False


@app.route('/', methods=["GET","POST"])
def index():
    error = ''
    uname = ''
    try:
        if request.method == 'POST':
            # TODO: (more) input sanitization...
            uname = request.form['username']
            passw = request.form['password']
            if not uname or not passw:
                raise Exception('Cannot provide an empty username or password!')

            # usrget = execute_query('SELECT password FROM flaskapp WHERE username=?', (uname,))
            hashed = bcrypt.hashpw(str(passw), app.config['SALT'])
            session['username'] = str(uname)
            session['hashed'] = str(hashed)
            if authenticate():
                return redirect(url_for('viewdb'))
            else:
                return redirect(url_for('register'))
    except Exception as e:
        error = e
    return render_template('index.html', error = error)


@app.route('/register', methods=["GET", "POST"])
def register():
    # TODO: format table (use html/css...)
    if not session['username'] or not session['hashed']:
        return '<h4>ERROR: username/hash not provided!?</h4>'
    error = ''
    try:
        uname = session['username']
        usrget = execute_query('SELECT username FROM flaskapp WHERE username=?', (uname,))
        if usrget:
            raise Exception('User "%s" already exists! cannot re-register!' % (uname))

        if request.method == 'POST':
            # TODO: input sanitization...
            fname = request.form['firstname']
            lname = request.form['lastname']
            email = request.form['email']

            sqlcmd = 'INSERT INTO flaskapp VALUES (?,?,?,?,?)'
            sqlargs = (session['username'], session['hashed'], fname, lname, email)
            conn = get_db()
            _ = conn.execute(sqlcmd, sqlargs)
            conn.commit()

            return redirect(url_for('viewdb'))
    except Exception as e:
        error = e
    return render_template('register.html', error = error)


@app.route('/viewdb')
def viewdb():
    # TODO: format table (use html/css...)
    error = ''
    try:
        if authenticate():
            columns = 'firstname,lastname,email'
            rows = execute_query('SELECT %s FROM flaskapp WHERE username=?' % (columns), (session['username'],))
            rows = [columns.split(',')] + rows
            return '<br>'.join(str(row) for row in rows)
        else:
            error = 'ERROR: user not found!'
    except Exception as e:
        error = e
    return '<h4>' + str(error) + '</h4>'



##########################
# COPY PASTA FROM TUTORIAL
# https://www.datasciencebytes.com/bytes/2015/02/28/using-flask-to-answer-sql-queries/

def connect_to_database():
    return sqlite3.connect(app.config['DATABASE'])

def get_db():
    db = getattr(g, 'db', None)
    if db is None:
        db = g.db = connect_to_database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()

def execute_query(query, args=()):
    cur = get_db().execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows
###########################


if __name__ == '__main__':
    # NOTE: this wont get hit if being used with mod_wsgi
    app.config['APP_PATH'] = os.path.abspath(os.path.dirname(__file__))
    app.config['DATABASE'] = app.config['APP_PATH'] + '/flaskapp.db'
    app.config['SALT_PATH'] = app.config['APP_PATH'] + '/salt.txt'
    app.config['SALT'] = ''
    with open(app.config['SALT_PATH'], 'r') as sp:
        app.config['SALT'] = sp.read()

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    #session.init_app(app)
    app.debug = True
    app.run()
