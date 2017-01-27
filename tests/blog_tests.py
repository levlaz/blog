import os
import sys
import unittest
import tempfile

sys.path.insert(0, os.environ.get('BLOG_PATH'))
from blog.blog import app, init_db

class BlogTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app.app_context():
            init_db()

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
        assert b'Lev\'s Hacking Notes' in rv.data
        assert b'Billy Bob Blog' not in rv.data

    def test_login_logout(self):
        rv = self.login('test')
        assert b'You were logged in' in rv.data
        rv = self.logout()
        assert b'You were logged out' in rv.data
        rv = self.login('wrong-password')
        assert b'Invalid password' in rv.data

if __name__ == '__main__':
    unittest.main()