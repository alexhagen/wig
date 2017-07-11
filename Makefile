all: docs publish

docs: FORCE
	pandoc README.md -o docs/README.rst; \
	make example; \
	cd docs; \
	sphinx-apidoc -e -f -M -o ./ ../wig/; \
	cd ~/code/wig/docs/; \
	make html

example: tests/example_wig.ipynb
	jupyter nbconvert ../tests/example_wig.ipynb --to html --template=basic --execute; \
	mv ../tests/example_wig.html example.html; \

publish: FORCE
	MSG="$(shell git log -1 --pretty=%B | tr -d '\n')"
	@echo $(MSG)
	cd ~/pages/wig/; \
	git rm -rf *; \
	cd ~/code/wig/docs/; \
	cp -r _build/html/* ~/pages/wig/; \
	cd ~/pages/wig; \
	touch .nojekyll; \
	git add *; \
	git add .nojekyll; \
	git commit -am "$(shell git log -1 --pretty=%B | tr -d '\n')"; \
	git push origin gh-pages; \
	cd ~/code/wig


FORCE:
