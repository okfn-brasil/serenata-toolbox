default: test

bootstrap:
	python setup.py develop

setup:

test:
	python -m unittest discover
