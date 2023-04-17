## The Makefile includes instructions on environment setup and lint tests
# Create and activate a virtual environment
# Install dependencies in requirements.txt
# Dockerfile should pass hadolint
# app.py should pass pylint
# (Optional) Build a simple integration test

setup:
	# Create python virtualenv & source it
	pip install virtualenv
	virtualenv .devops --python python3

install:
	# This should be run from inside a virtualenv
	pip install --upgrade pip && \
	pip install --require-virtualenv -r requirements.txt

test:
	# Additional, optional, tests could go here
	pytest -vv tests/*.py
	#python -m pytest --nbval notebook.ipynb

lint:
	# See local hadolint install instructions:   https://github.com/hadolint/hadolint
	# This is linter for Dockerfiles
	docker run --rm -i hadolint/hadolint < Dockerfile
	# This is a linter for Python source code linter: https://www.pylint.org/
	# This should be run from inside a virtualenv
	pylint --disable=R,C,W1203,W1202 app.py

all: install lint test
