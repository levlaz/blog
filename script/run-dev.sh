#!/bin/bash

export FLASK_APP=blog/blog.py
export FLASK_DEBUG=1
flask migrate
flask run