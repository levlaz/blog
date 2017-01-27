import os
import sqlite3
import markdown
import datetime
from collections import OrderedDict
from slugify import slugify
from flask import Flask
from flask import request
from flask import session
from flask import g
from flask import redirect
from flask import url_for
from flask import abort
from flask import render_template
from flask import flash
from flask import make_response
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.config.from_pyfile(os.path.join(app.root_path, 'settings.cfg'))

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'blog.db'),
))


def connect_db():
    """Connects to Database"""
    rv = sqlite3.connect(
            app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
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


@app.cli.command('genpass')
def generate_password_command():
    """Generates a salted password hash."""
    password = input('Please enter a secure password: ')
    password_hash = generate_password_hash(password, method="pbkdf2:sha512")
    print("Your password hash is:\n {0} \n \
        Add this hash to the app config".format(password_hash))


@app.route('/')
def index():
    db = get_db()
    cur = db.execute("SELECT * FROM posts ORDER BY created_date DESC LIMIT 25")
    posts = cur.fetchall()
    return render_template(
            'index.html',
            posts=posts,
            get_tags=get_tags,
            form_title="Add New Post")


@app.route('/archive')
def archive():
    db = get_db()
    raw_years = db.execute("""
        SELECT DISTINCT(strftime('%Y', created_date)) from posts \
        ORDER BY created_date DESC
        """).fetchall()

    posts = OrderedDict()

    for year in raw_years:
        posts[year[0]] = {'posts': []}

    raw_post = db.execute("""
        SELECT slug, title, created_date as 'date [timestamp]' \
        FROM posts ORDER BY created_date DESC \
        """)

    for post in raw_post:
        posts[str(post['date'].year)]['posts'].append(
                dict(slug=post['slug'], post_title=post['title']))

    return render_template('archive.html', posts=posts)


@app.route('/feed')
def gen_feed():
    db = get_db()
    cur = db.execute("SELECT * FROM posts ORDER BY created_date DESC LIMIT 25")
    posts = cur.fetchall()
    feed = render_template(
            'rss.xml',
            posts=posts,
            gen_date=datetime.datetime.utcnow())
    response = make_response(feed)
    response.headers['Content-Type'] = "application/xml"
    return response


@app.route('/<string:post_slug>')
def show_post(post_slug):
    db = get_db()
    post = db.execute(
        "SELECT * FROM posts WHERE slug = ?", [post_slug]).fetchone()
    if post:
        return render_template('post.html', post=post, get_tags=get_tags)
    else:
        abort(404)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_post(id):
    if not session.get('logged_in'):
        abort(401)

    db = get_db()
    cursor = db.cursor()

    if request.method == 'POST':

        # Prepare Post
        title = request.form['title']
        text_raw = request.form['text'].strip()
        slug = slugify(title)
        text_compiled = markdown.markdown(
                text_raw, extensions=[
                    'markdown.extensions.fenced_code',
                    'markdown.extensions.codehilite'])
        tags = request.form['tags'].split(',')

        cursor.execute("UPDATE posts \
                SET title = ?, \
                slug = ?, \
                text_raw = ?, \
                text_compiled = ? \
                WHERE id = ?", [title, slug, text_raw, text_compiled, id])
        db.commit()

        for tag in tags:
            existing_id = find_tag(tag.strip())
            if existing_id:
                cursor.execute("INSERT INTO posts_tags (post_id, tag_id) \
                    VALUES(?, ?)", [id, existing_id])
                db.commit()
            else:
                cursor.execute(
                        "INSERT INTO tags (tag) VALUES(?)", [tag.strip()])
                tag_id = cursor.lastrowid
                cursor.execute("INSERT INTO posts_tags (post_id, tag_id) \
                    VALUES(?, ?)", [id, tag_id])
                db.commit()

        flash('Post updated')
        return redirect(url_for('show_post', post_slug=slug))

    post = db.execute("SELECT * FROM posts WHERE id = ?", [id]).fetchone()
    tags = get_tags(post[0])
    csv_tags = ""
    for tag in tags:
        print(dir(tag))
        csv_tags.join("{0},".format(tag))
    return render_template('edit.html', post=post, tags=csv_tags)


@app.route('/delete/<int:id>')
def delete_post(id):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute("DELETE FROM posts WHERE id = ?", [id])
    db.commit()

    flash('Post deleted!')
    return redirect(url_for('index'))


@app.route('/tags')
def show_tags_list():
    db = get_db()
    tags = db.execute("""
        SELECT t.tag, COUNT(pt.tag_id) FROM tags t
            JOIN posts_tags pt on pt.tag_id = t.id
            GROUP BY t.tag
            ORDER BY COUNT(pt.tag_id) DESC""").fetchall()
    return render_template('tags_list.html', tags=tags)


@app.route('/tag/<string:tag>')
def show_posts_with_tag(tag):
    db = get_db()
    posts = db.execute("""
        SELECT * from posts p
            JOIN posts_tags pt on pt.post_id = p.id
            JOIN tags t on t.id = pt.tag_id
            WHERE t.tag = ?
            ORDER BY p.created_date DESC""", [tag]).fetchall()
    description = "Posts tagged: {0}".format(tag)
    return render_template(
            'tags.html',
            posts=posts,
            get_tags=get_tags,
            description=description)


@app.route('/add', methods=['POST'])
def add_post():
    if not session.get('logged_in'):
        abort(401)

    db = get_db()
    cursor = db.cursor()

    # Prepare Post
    title = request.form['title']
    text_raw = request.form['text'].strip()
    slug = slugify(title)
    text_compiled = markdown.markdown(
            text_raw, extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite'])
    tags = request.form['tags'].split(',')

    cursor.execute("INSERT INTO posts (title, slug, text_raw, text_compiled) \
        VALUES (?, ?, ?, ?)", [title, slug, text_raw, text_compiled])
    post_id = cursor.lastrowid
    db.commit()

    for tag in tags:
        existing_id = find_tag(tag.strip())
        if existing_id:
            cursor.execute("INSERT INTO posts_tags (post_id, tag_id) \
                VALUES(?, ?)", [post_id, existing_id])
            db.commit()
        else:
            cursor.execute("INSERT INTO tags (tag) VALUES(?)", [tag.strip()])
            tag_id = cursor.lastrowid
            cursor.execute("INSERT INTO posts_tags (post_id, tag_id) \
                VALUES(?, ?)", [post_id, tag_id])
            db.commit()

    flash('New post added!')
    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if not verify_password(request.form['password']):
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


def find_tag(tag):
    db = get_db()
    cur = db.execute("SELECT id FROM tags WHERE tag = ?", [tag]).fetchone()
    if cur:
        return cur[0]


def get_tags(post_id):
    db = get_db()
    cur = db.execute("""
        SELECT tag FROM tags t
            JOIN posts_tags pt ON t.id = pt.tag_id
            JOIN posts p ON p.id = pt.post_id
            WHERE p.id = ?""", [post_id]).fetchall()
    return cur


def verify_password(password):
    return check_password_hash(app.config['PASSWORD'], password)


if __name__ == "__main__":
    app.run()
