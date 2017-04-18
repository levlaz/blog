#!/bin/bash

export FLASK_APP=blog/blog.py
flask migrate
flask run --host='0.0.0.0'
