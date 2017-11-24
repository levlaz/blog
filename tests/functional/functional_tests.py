import os
import sys
import tempfile
import unittest

from pyvirtualdisplay import Display
from selenium import webdriver
from urllib.request import urlopen

sys.path.insert(0, os.environ.get('BLOG_PATH'))
from blog.blog import app

class FunctionalTestCase(unittest.TestCase):

    def setUp(self):
        self.baseURL = "http://localhost:5000/"

        if os.getenv('CIRCLECI'):
            # Some additional stuff is requried in order to get this
            # to work on CI. I am sure there is a cleaner way to
            # do this, but this approach just works.
            self.display = Display(visible=0, size=(1920, 1080)).start()
            self.caps = webdriver.DesiredCapabilities().FIREFOX
            self.caps["marionette"] = False
            self.browser = webdriver.Firefox(capabilities=self.caps)
            self.browser.maximize_window()
            self.browser.implicitly_wait(10)
        else:
            self.browser = webdriver.Firefox()
            self.browser.implicitly_wait(10)

    def tearDown(self):
        self.browser.quit()

    def test_basics(self):
        """Basic RealityCheck to make sure that the app loads and the
        tests are working as expected."""
        # when I go to the main website
        self.browser.get(self.baseURL)

        # I see that the page loads
        self.assertIn('levlaz/blog', self.browser.page_source)

    def test_admin(self):
        # If I am an admin user
        # when I go to the login page
        self.browser.get(self.baseURL)
        self.browser.find_element_by_xpath('/html/body/nav/a[5]').click()

        # I see a Log In Form
        self.assertIn('Log In', self.browser.page_source)

        # When I submit an invalid password
        self.browser.find_element_by_xpath('/html/body/form/input[1]').send_keys('invalid')
        self.browser.find_element_by_xpath('/html/body/form/input[2]').click()

        # I see an error message
        error_message = self.browser.find_element_by_xpath('/html/body/p').text
        self.assertEqual('Invalid password', error_message)

if __name__ == '__main__':
    unittest.main()
