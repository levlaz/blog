import os
import sys
import tempfile
import unittest

from selenium import webdriver
from urllib.request import urlopen

sys.path.insert(0, os.environ.get('BLOG_PATH'))
from blog.blog import app

class FunctionalTestCase(unittest.TestCase):

    def setUp(self):
        self.driver = webdriver.Chrome()
        self.baseURL = "http://localhost:5000/"

    def tearDown(self):
        self.driver.quit()

    def test_home(self):
        self.driver.get(self.baseURL)
        # FIXME get webdriver to work
        assert True


if __name__ == '__main__':
    unittest.main()
