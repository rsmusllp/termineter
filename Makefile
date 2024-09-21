VERSION := $(shell ./setup.py --version)

.PHONY: build
build:
	python setup.py build sdist

.PHONY: clean
clean:
	rm -rf build dist

.PHONY: release
release: build
	$(eval RELEASE_TAG := v$(VERSION))
	git tag -sm "Version $(VERSION)" $(RELEASE_TAG)
	git push --tags
	twine upload dist/*
