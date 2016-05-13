all: test

filename=speakers-`python -c 'import speakers.version;print speakers.version.version'`.tar.gz

export PYTHONPATH:=  ${PWD}

test: clean
	@echo "Running tests"
	@nosetests --cover-branches --with-coverage  --cover-erase --cover-package=speakers --stop -v -s tests
	@cd docs && make html

docs: clean
	@steadymark docs/*.md
	@git co master && \
		(git br -D gh-pages || printf "") && \
		git checkout --orphan gh-pages && \
		markment -o . -t theme docs --sitemap-for=http://falcao.it/speakers && \
		cp quick-start.html index.html && \
		git add . && \
		git commit -am 'documentation' && \
		git push --force origin gh-pages && \
		git checkout master
clean:
	@printf "Cleaning up files that are already in .gitignore... "
	@for pattern in `cat .gitignore`; do rm -rf $$pattern; find . -name "$$pattern" -exec rm -rf {} \;; done
	@echo "OK!"

release: test
	@./.release
	@python setup.py sdist register upload
