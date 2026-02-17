# russellane/Python.mk

VENV ?=		.venv

build::		venv tags lint test doc dist

lint::		black isort flake8
test::		pytest
doc::		;
dist::
		pdm build

PROJECT_NAME := $(shell sed -ne 's/^name = "\(.*\)"$$/\1/p' pyproject.toml)

.PHONY:		venv
venv:		$(VENV)
$(VENV):
		pdm install

.PHONY:		tags
tags::
		ctags -R $(PROJECT) tests $(VENV)

black::
		pdm run black -q $(PROJECT) tests

isort::
		pdm run isort $(PROJECT) tests

flake8::
		pdm run flake8 $(PROJECT) tests

mypy::
		pdm run mypy $(PROJECT) tests

COV_FAIL_UNDER = 0
PYTEST =	pdm run pytest $(PYTESTOPTS) \
		--cov=$(PROJECT) --cov-report=html \
		--cov-fail-under $(COV_FAIL_UNDER) \
		--exitfirst --showlocals --verbose

pytest::
		$(PYTEST) tests

pytest_debug::
		$(PYTEST) --capture=no tests

coverage::
		pdm run pytest --cov=$(PROJECT) tests

install::
		-pipx uninstall $(PROJECT_NAME)
		pipx install .

publish_local::
		cd dist; echo *.whl | cpio -pdmuv `pip config get global.find-links`

publish_test::
		twine upload --verbose -r testpypi dist/*

publish_prod::
		twine upload --verbose -r pypi dist/*

clean::
		rm -rf .coverage .mypy_cache .pdm-build .pytest_cache $(VENV) dist htmlcov tags
		find . -type f -name '*.py[co]' -delete
		find . -type d -name __pycache__ -delete

# put `doc :: README.md` into Makefile, if desired
.PHONY:		README.md
README.md:
		pdm run python -m $(PROJECT) --md-help >$@

# vim: set ts=8 sw=8 noet:
