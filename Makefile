.PHONY: test

test:
	export BLOG_PATH=$(pwd) && coverage run --source blog -m unittest tests/**.py
	coverage html

shell:
	export FLASK_APP=blog/blog.py && export FLASK_DEBUG=1 && flask shell

dev:
	export FLASK_APP=blog/blog.py && export FLASK_DEBUG=1 && flask migrate && flask run