.PHONY: install lint test build clean dist codacy

CODACY_PROJECT_TOKEN?=fake
PYTHON_VERSION?=default
REGISTRY?=886366864302.dkr.ecr.eu-west-1.amazonaws.com
VERSION?=0.0.0

install:
	@echo "# --pre allows pre releases"
	pip install --pre -e .
	pip install -r requirements-dev.txt

lint:
	flake8 thunderstorm test

test: lint
	pytest \
		-vv \
		--cov thunderstorm \
		--cov-report xml:coverage-${PYTHON_VERSION}.xml \
		--cov-append \
		--junit-xml results-${PYTHON_VERSION}.xml \
		test/

build:
	pip install -e .

clean:
	rm -rf dist

dist: clean
	python setup.py sdist

codacy:
	python-codacy-coverage -r coverage-${PYTHON_VERSION}.xml
