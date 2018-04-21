tests: deps
	pipenv run nosetests tests --rednose

deps:
	@pipenv install --dev
	@pipenv run python setup.py develop


html-docs:
	cd docs && make html

docs: html-docs
	open docs/build/html/index.html

release:
	@rm -rf dist/*
	@./.release
	@make pypi

pypi:
	@pipenv run python setup.py build sdist
	@pipenv run twine upload dist/*.tar.gz

tox:
	@pipenv run tox

.PHONY: docs tests
