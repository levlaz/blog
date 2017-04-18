import os
import sys
import unittest
import tempfile
import sqlite3

sys.path.insert(0, os.environ.get('BLOG_PATH'))
from blog.blog import app, migrate_db, cache

class BlogTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app.app_context():
            cache.clear()
            migrate_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])

    def login(self, password):
        return self.app.post('/login', data=dict(
            password=password
        ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_empty(self):
        rv = self.app.get('/')
        assert b'CircleCI Docker Demo' in rv.data
        assert b'Billy Bob Blog' not in rv.data

    def test_login_logout(self):
        rv = self.login('test')
        assert "You were logged in" in rv.get_data(as_text=True)
        cache.clear()
        rv = self.logout()
        assert 'You were logged out' in rv.get_data(as_text=True)
        rv = self.login('wrong-password')
        assert b'Invalid password' in rv.data

    def test_unique_posts_tags(self):
        rv = self.login('test')
        rv = self.app.post('/add', data=dict(
            title="Test Title",
            text="This is some test text",
            tags="test1, test2, test3"), follow_redirects=True)

        with self.assertRaises(sqlite3.IntegrityError):
            rv = self.app.post('/edit/1', data=dict(
                title="Test Title",
                text="New Text",
                tags="test1, test2"), follow_redirects=True)


if __name__ == '__main__':
    unittest.main()
