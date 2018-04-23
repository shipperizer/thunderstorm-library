.PHONY: install lint test build clean dist release codacy

CODACY_PROJECT_TOKEN?=fake
PYTHON_VERSION?=default
REGISTRY?=docker.io

install:
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

lint:
	flake8 thunderstorm test

test: lint
	pytest \
		--cov thunderstorm \
		--cov-report xml \
		--cov-append \
		--junit-xml results-${PYTHON_VERSION}.xml \
		test/

build:
	pip install -e .

clean:
	rm -rf dist

dist: clean
	python setup.py sdist

release: dist
	git tag v$$(python setup.py --version)
	git push --tags
	github-release release \
		--user artsalliancemedia \
		--repo thunderstorm-library \
		--tag v$$(python setup.py --version) \
		--pre-release
	github-release upload \
		--user artsalliancemedia \
		--repo thunderstorm-library \
		--tag v$$(python setup.py --version) \
		--name thunderstorm-library-$$(python setup.py --version).tar.gz \
		--file dist/thunderstorm-library-$$(python setup.py --version).tar.gz

codacy:
	python-codacy-coverage -r coverage.xml


python34:
	docker build --tag ${REGISTRY}/artsalliancemedia/python:3.4-slim -f config/Dockerfile34 .

python35:
	docker build --tag ${REGISTRY}/artsalliancemedia/python:3.5-slim -f config/Dockerfile35 .

python36:
	docker build --tag ${REGISTRY}/artsalliancemedia/python:3.6-slim -f config/Dockerfile36 .

push:
	docker push ${REGISTRY}/artsalliancemedia/python:3.4-slim
	docker push ${REGISTRY}/artsalliancemedia/python:3.5-slim
	docker push ${REGISTRY}/artsalliancemedia/python:3.6-slim
