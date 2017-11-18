import os
import sys
import tempfile
import unittest

from blog.blog import *

sys.path.insert(0, os.environ.get('BLOG_PATH'))

class BlogUnitTestCase(unittest.TestCase):

    def test_connect_db(self):
        db = connect_db()
        assert isinstance(db, sqlite3.Connection)

    def test_get_db(self):
        self.db, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app.app_context():
            db = get_db()
            assert isinstance(db, sqlite3.Connection)

            def schema():
                return db.execute("SELECT * FROM sqlite_master").fetchall()

            assert len(schema()) == 0

            init = migrate_db()

            assert len(schema()) == 22

    def test_get_static_pages(self):
        self.db, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app.app_context():
            migrate_db()
            db = get_db()
            assert len(get_static_pages()) == 0
            cur = db.cursor()
            cur.execute("""
                INSERT INTO posts (title, slug, text_raw, text_compiled, is_static_page) \
                VALUES("Static 1", "static-1", "", "", 0)
                """)
            cur.execute("""
                INSERT INTO posts (title, slug, text_raw, text_compiled, is_static_page) \
                VALUES("Static 2", "static-2", "", "", 0)
                """)
            cur.execute("""
                INSERT INTO posts (title, slug, text_raw, text_compiled, is_static_page) \
                VALUES("Static 3", "static-3", "", "", 0)
                """)
            db.commit()

            assert len(get_static_pages()) == 3

            cur.execute("""
                INSERT INTO posts (title, slug, text_raw, text_compiled) \
                VALUES("Post 1", "post-1", "", "")
                """)
            cur.execute("""
                INSERT INTO posts (title, slug, text_raw, text_compiled) \
                VALUES("Post 2", "post-2", "", "")
                """)
            cur.execute("""
                INSERT INTO posts (title, slug, text_raw, text_compiled) \
                VALUES("Post 3", "post-3", "", "")
                """)
            db.commit()

            posts = cur.execute("SELECT * FROM posts WHERE is_static_page = 1").fetchall()

            assert len(posts) == 3
            assert len(get_static_pages()) == 3

            posts_and_pages = cur.execute("SELECT * FROM posts").fetchall()
            assert len(posts_and_pages) == 6


if __name__ == '__main__':
    unittest.main()
