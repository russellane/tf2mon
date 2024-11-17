# russellane/Python.mk

build::		__pypackages__ tags lint test doc
		pdm build

lint::		black isort flake8
test::		pytest
doc::		;

bump_micro::	_bump_micro clean build
_bump_micro:
		pdm bump micro

publish_local::
		cd dist; echo *.whl | cpio -pdmuv `pip config get global.find-links`

publish_test::
		twine upload --verbose -r testpypi dist/*

publish_prod::
		twine upload --verbose -r pypi dist/*

PROJECT_NAME := $(shell sed -ne 's/^name = "\(.*\)"$$/\1/p' pyproject.toml)
install::
		-pipx uninstall $(PROJECT_NAME)
		pipx install $(PROJECT_NAME)

__pypackages__:
		pdm install

.PHONY:		tags
tags::
		ctags -R $(PROJECT) tests __pypackages__ 

black::
		python -m black -q $(PROJECT) tests

isort::
		python -m isort $(PROJECT) tests

flake8::
		python -m flake8 $(PROJECT) tests

mypy::
		python -m mypy $(PROJECT) tests

COV_FAIL_UNDER = 0
PYTEST =	python -m pytest $(PYTESTOPTS) \
		--cov=$(PROJECT) --cov-report=html \
		--cov-fail-under $(COV_FAIL_UNDER) \
		--exitfirst --showlocals --verbose

pytest::
		$(PYTEST) tests

pytest_debug::
		$(PYTEST) --capture=no tests

coverage::
		python -m pytest --cov=$(PROJECT) tests

clean::
		rm -rf .coverage .mypy_cache .pdm-build .pytest_cache __pypackages__ dist htmlcov tags 
		find . -type f -name '*.py[co]' -delete
		find . -type d -name __pycache__ -delete

# put `doc :: README.md` into Makefile, if desired
.PHONY:		README.md
README.md:
		python -m $(PROJECT) --md-help >$@

# vim: set ts=8 sw=8 noet:
