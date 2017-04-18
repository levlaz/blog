import os
import sys
import unittest
import tempfile
import xmlrunner

sys.path.insert(0, os.environ.get('BLOG_PATH'))
from blog.blog import *

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

            assert len(schema()) == 21

if __name__ == '__main__':
    unittest.main(testRunner=xmlrunner.XMLTestRunner(output='test-reports'))
