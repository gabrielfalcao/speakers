all: test

filename=speakers-`python -c 'import speakers.version;print speakers.version.version'`.tar.gz

export PYTHONPATH:=  ${PWD}

test: clean
	@echo "Running tests"
	@nosetests --cover-branches --with-coverage  --cover-erase --cover-package=speakers --stop -v -s tests
	@steadymark README.md
	@steadymark docs/*.md
docs: clean
	@steadymark docs/*.md
	@git co gh-pages && git merge master && markment -o . -t theme docs && git add . && git commit -am 'documentation' && git push
clean:
	@printf "Cleaning up files that are already in .gitignore... "
	@for pattern in `cat .gitignore`; do rm -rf $$pattern; find . -name "$$pattern" -exec rm -rf {} \;; done
	@echo "OK!"

release: test
	@./.release
	@python setup.py sdist register upload
