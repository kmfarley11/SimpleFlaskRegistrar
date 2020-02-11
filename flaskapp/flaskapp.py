#######################################################################################
# flaskapp.py
#   houses the main web server code for assignment #1
#   urls = 
#       '/'         : the sign in page (enter a username & password)
#       '/register' : if a new username was entered from '/', prompts for more info
#       '/viewdb'   : post register/signin with a stored username displays user info
#
#   Note: the sign in and register pages are the main '/' page. I did not see a need
#       to separate the two: 
#           if an existing user with a valid password, show data
#           if an existing user with an invalid password, show error
#           if new user, redirect to final registration input
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
    DATABASE = os.path.join(APP_PATH, 'flaskapp.db')
    SALT_PATH = os.path.join(APP_PATH, 'salt.txt')
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


# generic input sanitization
def sanitize(to_check):
    invalid_chars = '\'"\\' # ' " \
    char_limit = 50
    if any([c in invalid_chars for c in to_check]) or len(to_check) > char_limit:
        raise Exception('Invalid input detected! Omit quote and escape characters. Also use less than %d chars.' % (char_limit))
    if not to_check.strip():
        raise Exception('Empty inputs are not allowed!')
    return to_check.strip()


@app.route('/', methods=["GET","POST"])
def index():
    error, uname = '', ''
    try:
        if request.method == 'POST':
            # sanitize inputs, hash password, store session data (user,hash)
            uname = sanitize(request.form['username'])
            passw = sanitize(request.form['password'])
            hashed = bcrypt.hashpw(str(passw), app.config['SALT'])
            session['username'] = str(uname)
            session['hashed'] = str(hashed)
            # authenticate uses session data
            if authenticate():
                return redirect(url_for('viewdb'))
            else:
                return redirect(url_for('register'))
    except Exception as e:
        error = e
    return render_template('index.html', error = error)


@app.route('/register', methods=["GET", "POST"])
def register():
    error = ''
    try:
        if not session['username'] or not session['hashed']:
            raise Exception('username/hash not provided, cannot submit...!?')

        uname = session['username']
        usrget = execute_query('SELECT username FROM flaskapp WHERE username=?', (uname,))
        if usrget:
            raise Exception('User "%s" already exists! cannot re-register!' % (uname))

        if request.method == 'POST':
            fname = sanitize(request.form['firstname'])
            lname = sanitize(request.form['lastname'])
            email = sanitize(request.form['email'])

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
    error, py_html = '', ''
    try:
        if authenticate():
            # Note: html construction here is a little hacky
            columns = 'firstname,lastname,email'
            rows = execute_query('SELECT %s FROM flaskapp WHERE username=?' % (columns), (session['username'],))
            html_columns = '<tr>' + ''.join(['<th>'+r+'</th>' for r in columns.split(',')]) + '</tr>' 
            html_rows = ''.join(['<tr>' + ''.join(['<td>'+r+'</td>' for r in row]) + '</tr>' for row in rows])
            py_html = '<table>' + html_columns + html_rows + '</table>'
        else:
            error = 'user "%s" not found!' % (session['username'])
    except Exception as e:
        error = e
    return render_template('viewdb.html', py_html = py_html, error = error)



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
    app.config['DATABASE'] = os.path.join(app.config['APP_PATH'], 'flaskapp.db')
    app.config['SALT_PATH'] = os.path.join(app.config['APP_PATH'], 'salt.txt')
    app.config['SALT'] = ''
    with open(app.config['SALT_PATH'], 'r') as sp:
        app.config['SALT'] = sp.read()

    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    #session.init_app(app)
    app.debug = True
    app.run()
