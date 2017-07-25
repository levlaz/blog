import unittest
import os
import sys

from flask_testing import LiveServerTestCase
from selenium import webdriver
from urllib.request import urlopen

sys.path.insert(0, os.environ.get('BLOG_PATH'))
from blog.blog import app

class FunctionalTestCase(LiveServerTestCase):

    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        with app.app_context():
            cache.clear()
            migrate_db()

        self.driver = webdriver.Chrome()
        self.driver.get(self.get_server_url())

    def tearDown(self):
        self.driver.quit()

    def test_server_is_up_and_running(self):
        res = urlopen(self.get_server_url())
        self.assertEqual(res.code, 200)

if __name__ == '__main__':
    unittest.main()
