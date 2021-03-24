# blog
Lev's Personal Blog

[![CI](https://circleci.com/gh/levlaz/blog.svg?style=shield&circle-token=:circle-token)](https://circleci.com/gh/levlaz/blog)

levlaz/blog (for lack of a better name) is a simple, ugly, single user blogging application written in Python and Flask.

## Table of Contents

* [Features](#) <!-- TODO -->
* [Installation](#installation)
* [Deploying to Production](#) <!-- TODO -->
* [Development](#development)

## Installation

### Dependencies

* Python 3.5.2
* SQLite 3.11.0
* Python modules listed in [`requirements.txt`](https://github.com/levlaz/blog/blob/master/requirements.txt)

## Development

You can install all dependencies (including testing and dev-only dependencies) by running `pip install -r dev-requirements.txt`. I suggest using a [virtualenv](https://pypi.python.org/pypi/virtualenv) in order to not pollute your global python.

### Coding Style

This project follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code. CI tests will fail if your code does not adhere to this spec. You can test to make sure that all of your code is PEP 8 compliant by running `flake8 blog` from the project root.

### Running Tests

This project aims to have a robust test suite and 100% code coverage. In order to run the existing tests you can run `export BLOG_PATH=$(pwd) && coverage run --source blog -m unittest tests/**.py` from the project root.

If you wish to test a single test from the tests/ directory then you can run `export BLOG_PATH=$(pwd) && python -m unittest tests/$SINGLE_FILE.py`

If you add new code to this project, please write the corresponding unit and integration tests and ensure that they pass.
