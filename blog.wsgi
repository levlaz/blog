#!/usr/bin/env python3
import sys

activate_this = '/var/www/blog/env/bin/activate_this.py'
with open(activate_this) as file_:
	exec(file_.read(), dict(__file__=activate_this))

sys.path.insert(0, '/var/www/blog')
from blog import app as application
