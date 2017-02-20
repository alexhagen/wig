all: docs

docs: FORCE
	MSG="$(shell git log -1 --pretty=%B | tr -d '\n')"
	@echo $(MSG)
	pandoc README.md -o docs/README.rst; \
	cd docs/; \
	sphinx-apidoc -e -f -M -o ./ ../wig/; \
	cd ~/pages/wig/; \
	git rm -r *; \
	cd ~/code/wig/docs/; \
	make html; \
	cp -r _build/html/* ~/pages/wig/; \
	cd ~/pages/wig; \
	touch .nojekyll; \
	git add *; \
	git add .nojekyll; \
	git commit -am "$(shell git log -1 --pretty=%B | tr -d '\n')"; \
	git push origin gh-pages; \
	cd ~/code/wig

FORCE:
