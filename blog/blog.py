import os
import sqlite3
from flask import Flask
from flask import request
from flask import session
from flask import g
from flask import redirect
from flask import url_for
from flask import abort
from flask import render_template
from flask import flash

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'blog.db'),
    SECRET_KEY='super secret',
    USERNAME='admin',
    PASSWORD='password'
))
app.config.from_envvar('BLOG_SETTINGS', silent=True)

def connect_db():
    """Connects to Database"""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    """Opens new db connection if there is not an 
    existing one for the current app ctx.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.teardown_appcontext
def close_db(error):
    """Closes db at the end of request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print("Initialized the database.")

""" Views """
@app.route('/')
def index():
    db = get_db()
    cur = db.execute("SELECT title, text FROM posts ORDER BY created_date DESC")
    posts = cur.fetchall()
    return render_template('index.html', posts=posts)

@app.route('/add', methods=['POST'])
def add_post():
    if not session.get('logged_in'):
        print(request.form)
        abort(401)
    db = get_db()
    raw_text = request.form['text']
    formatted_text = raw_text.replace('\r\n', '<br />')
    print(formatted_text)
    db.execute("INSERT INTO posts (title, text) VALUES (?, ?)",
            [request.form['title'], formatted_text])
    db.commit()
    flash('New post added!')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Invalid Username'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('index'))
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('index'))
