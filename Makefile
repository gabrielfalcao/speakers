deps:
	@(2>&1 which pipenv > /dev/null) || pip install pipenv
	@pipenv install --dev
	@pipenv run python setup.py develop

tests:
	pipenv run nosetests tests --rednose

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

.PHONY: docs tests
