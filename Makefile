.PHONY: test

test:
	export BLOG_PATH=$(pwd) && coverage run --source blog -m unittest tests/**.py
	coverage html