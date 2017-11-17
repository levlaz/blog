# -*- coding: utf-8 -*-
"""
levlaz/blog

Simple blogging engine written in python and Flask

:copyright: (c) 2017 by Lev Lazinskiy
:license: MIT, see LICENSE for more details.
"""
import datetime
import os
import sqlite3
from collections import OrderedDict
from threading import Thread

import markdown
from flask import (Flask, abort, current_app, flash, g, make_response,
                   redirect, render_template, request, session, url_for)
from flask_cache import Cache
from flask_mail import Mail, Message
from slugify import slugify
from werkzeug.security import check_password_hash, generate_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

app = Flask(__name__)
cache = Cache(app, config={
    'CACHE_TYPE': 'simple',
    'CACHE_DEFAULT_TIMEOUT': 3600})
mail = Mail()

app.config.from_pyfile(os.path.join(app.root_path, 'settings.cfg'))

app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'blog.db'),
))

mail.init_app(app)

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


def migrate_db():
    db = get_db()
    dir = os.path.dirname(__file__)
    migrations_path = os.path.join(dir, 'migrations/')
    migration_files = list(os.listdir(migrations_path))
    for migration in sorted(migration_files):
        path = "migrations/{0}".format(migration)
        with app.open_resource(path, mode='r') as f:
            db.cursor().executescript(f.read())


def generate_confirmation_token(comment_id, expiration=3600):
    s = Serializer(current_app.config['SECRET_KEY'], expiration)
    return s.dumps({'confirm': comment_id})


def confirm(comment_id, token):
    s = Serializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token)
    except:
        return False
    if data.get('confirm') != int(comment_id):
        return False
    return True


# Email Functions
def send_async_email(app, msg):
    """Send Mail in App Context

    Args:
        app: current flask app
        msg: the mail message
    """
    with app.app_context():
        mail.send(msg)


def send_email(to, subject, template, **kwargs):
    """Send email message on a new thread"""
    app = current_app._get_current_object()
    msg = Message(subject, recipients=[to])
    msg.body = render_template(template, **kwargs)
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    return thr


@app.teardown_appcontext
def close_db(error):
    """Closes db at the end of request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.cli.command('migrate')
def migratedb_commant():
    """Runs all database migrations."""
    migrate_db()
    print("Ran all Migrations.")


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
    cur = db.execute(
        "SELECT * FROM posts \
        WHERE is_static_page != 0 \
        ORDER BY created_date DESC LIMIT 25")
    posts = cur.fetchall()
    return render_template(
            'index.html',
            posts=posts,
            get_tags=get_tags,
            form_title="Add New Post")


@app.route('/search/')
def search():
    query = request.args.get('query')
    db = get_db()
    results = db.execute("""
        SELECT fts.docid, p.slug, p.title, p.text_raw FROM full_text_search fts
        JOIN posts p on p.id = fts.docid
        WHERE full_text_search MATCH ?""", [query]).fetchall()

    return render_template('search_results.html', query=query, results=results)


@app.route('/archive/')
@cache.cached()
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
        FROM posts
        WHERE is_static_page != 0
        ORDER BY created_date DESC \
        """)

    for post in raw_post:
        posts[str(post['date'].year)]['posts'].append(
                dict(slug=post['slug'], post_title=post['title']))

    return render_template('archive.html', posts=posts)


@app.route('/feed/')
@cache.cached()
def gen_feed():
    db = get_db()
    cur = db.execute(
        "SELECT * FROM posts \
        WHERE is_static_page != 0 \
        ORDER BY created_date DESC LIMIT 25")
    posts = cur.fetchall()
    feed = render_template(
            'rss.xml',
            posts=posts,
            gen_date=datetime.datetime.utcnow())
    response = make_response(feed)
    response.headers['Content-Type'] = "application/xml"
    return response


@app.route('/<string:post_slug>/')
def show_post(post_slug):
    db = get_db()
    post = db.execute(
        "SELECT * FROM posts WHERE slug = ?", [post_slug]).fetchone()
    if (post['is_static_page'] == 0):
        return render_template('page.html', post=post)
    elif post:
        return render_template(
            'post.html',
            post=post,
            get_tags=get_tags,
            get_comments=get_comments,
            get_comment_count=get_comment_count)
    else:
        abort(404)


@app.route('/edit/<int:id>/', methods=['GET', 'POST'])
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
            if len(tag.strip()) != 0:
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

        cache.clear()
        flash('Post updated')
        return redirect(url_for('show_post', post_slug=slug))

    post = db.execute("SELECT * FROM posts WHERE id = ?", [id]).fetchone()
    tags = get_tags(post[0])
    csv_tags = ""
    for tag in tags:
        csv_tags.join("{0},".format(tag))
    return render_template('edit.html', post=post, tags=csv_tags)


@app.route('/delete/<int:id>/')
def delete_post(id):
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute("DELETE FROM posts WHERE id = ?", [id])
    db.commit()

    flash('Post deleted!')
    return redirect(url_for('index'))


@app.route('/tags/')
@cache.cached()
def show_tags_list():
    db = get_db()
    tags = db.execute("""
        SELECT t.tag, COUNT(pt.tag_id) FROM tags t
            JOIN posts_tags pt on pt.tag_id = t.id
            GROUP BY t.tag
            ORDER BY COUNT(pt.tag_id) DESC""").fetchall()
    return render_template('tags_list.html', tags=tags)


@app.route('/tag/<string:tag>/')
@cache.cached()
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
    page = 'page' in request.form

    cursor.execute("INSERT INTO posts (title, slug, text_raw, text_compiled) \
        VALUES (?, ?, ?, ?)", [title, slug, text_raw, text_compiled])
    post_id = cursor.lastrowid
    db.commit()

    if page:
        cursor.execute(
            "UPDATE posts SET is_static_page = 0 WHERE id = ?", (post_id,))
        db.commit()

    for tag in tags:
        if len(tag.strip()) != 0:
            existing_id = find_tag(tag.strip())
            if existing_id:
                cursor.execute("INSERT INTO posts_tags (post_id, tag_id) \
                    VALUES(?, ?)", [post_id, existing_id])
                db.commit()
            else:
                cursor.execute(
                    "INSERT INTO tags (tag) VALUES(?)", [tag.strip()])
                tag_id = cursor.lastrowid
                cursor.execute("INSERT INTO posts_tags (post_id, tag_id) \
                    VALUES(?, ?)", [post_id, tag_id])
                db.commit()

    flash('New post added!')
    return redirect(url_for('index'))


@app.route('/comment/<int:id>', methods=['POST'])
def add_comment(id):
    """Add comment to a post"""
    db = get_db()
    cursor = db.cursor()

    # Prepare comment
    author = request.form['author']
    email = request.form['email']
    website = request.form['website']
    comment_body = request.form['comment_body']

    cursor.execute("INSERT INTO comments (post_id, author, email, website, comment_body) \
        VALUES (?, ?, ?, ?, ?)", [id, author, email, website, comment_body])
    comment_id = cursor.lastrowid
    print(comment_id)
    db.commit()

    flash("Your comment has been added, once it has been approved it will appear on this post page.")

    post = get_post(id)

    subject = "New comment on {0}".format(post['title'])
    token = generate_confirmation_token(comment_id)

    send_email(
        app.config['ADMIN_EMAIL'],
        subject,
        'mail/comment',
        post = post['title'],
        author = author,
        body = comment_body,
        comment_id = comment_id,
        token=token)

    return redirect(request.referrer)


@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if not verify_password(request.form['password']):
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            cache.clear()
            return redirect(url_for('index'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    cache.clear()
    return redirect(url_for('index'))


@app.route('/approve_comment/<comment_id>/<token>')
def approve_comment(comment_id, token):
    if confirm(comment_id, token):
        db = get_db()
        cur = db.execute("""
            UPDATE comments
            SET is_visible=1
            WHERE id = ?""", [comment_id])
        db.commit()
        flash('Comment approved')
        return redirect(url_for('index'))
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('index'))


def find_tag(tag):
    db = get_db()
    cur = db.execute("SELECT id FROM tags WHERE tag = ?", [tag]).fetchone()
    if cur:
        return cur[0]

def get_post(post_id):
    db = get_db()
    cur = db.execute("""
        SELECT * FROM posts
        WHERE posts.id = ?""", [post_id]).fetchone()
    return cur

def get_tags(post_id):
    db = get_db()
    cur = db.execute("""
        SELECT tag FROM tags t
            JOIN posts_tags pt ON t.id = pt.tag_id
            JOIN posts p ON p.id = pt.post_id
            WHERE p.id = ?""", [post_id]).fetchall()
    return cur


def get_static_pages():
    db = get_db()
    cur = db.execute("""
        SELECT * FROM posts
        WHERE is_static_page = 0
        """).fetchall()
    return cur


def get_comments(post_id):
    """Get comments for a post."""
    db = get_db()
    cur = db.execute("""
        SELECT * FROM comments
        WHERE is_visible = 1 AND post_id = ?""", [post_id]).fetchall()
    return cur


def get_comment_count(post_id):
    """Get count of comments for a post."""
    db = get_db()
    cur = db.execute("""
        SELECT COUNT(id) FROM comments
        WHERE is_visible = 1 AND post_id = ?""", [post_id]).fetchone()
    return cur[0]


app.jinja_env.globals.update(get_static_pages=get_static_pages)


def verify_password(password):
    return check_password_hash(app.config['PASSWORD'], password)


if __name__ == "__main__":
    app.run()
