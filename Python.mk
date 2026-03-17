# russellane/Python.mk

VENV ?=		.venv

# Full pipeline (lint → test → dist); default target, run before publish_prod.
build::		venv tags lint test doc dist

lint::		ruff
test::		pytest
doc::		;

# Build wheel only; step 1 of each iteration cycle (app or lib).
dist::
		pdm build

PROJECT_NAME := $(shell sed -ne 's/^name = "\(.*\)"$$/\1/p' pyproject.toml)
PACKAGES =	$(shell pip config get global.find-links)

.PHONY:		venv
venv:		$(VENV)
$(VENV):
		pdm install

.PHONY:		tags
tags::
		ctags -R $(PROJECT) tests $(VENV)

ruff::
		pdm run ruff format $(PROJECT) tests
		pdm run ruff check --fix $(PROJECT) tests

mypy::
		pdm run mypy $(PROJECT) tests

# coverage fail_under is set in pyproject.toml [tool.coverage.report]
PYTEST =	pdm run pytest $(PYTESTOPTS) \
		--cov=$(PROJECT) --cov-report=html \
		--exitfirst --showlocals --verbose

pytest::
		$(PYTEST) tests

pytest_debug::
		$(PYTEST) --capture=no tests

coverage::
		pdm run pytest --cov=$(PROJECT) tests

# Apps: install/re-install from local dist; use during iteration and to verify after publish_prod.
# (Libs neuter this target.)
install::
		pipx install --force .

# Libs: deploy wheel to ~/packages; run after make dist during lib iteration.
publish_local::
		cd dist; echo *.whl | cpio -pdmuv $(PACKAGES)

# Libs: remove this project's wheels from ~/packages after publish_prod.
clean_local::
		rm -f $(PACKAGES)/$(subst -,_,$(PROJECT_NAME))-*.whl

# TestPyPI: machinery health check only, not a functional test gate.
publish_test::
		twine upload --verbose -r testpypi dist/*

# Final publish to PyPI.
publish_prod::
		twine upload --verbose -r pypi dist/*

clean::
		rm -rf .coverage .mypy_cache .pdm-build .pytest_cache $(VENV) dist htmlcov tags
		find . -type f -name '*.py[co]' -delete
		find . -type d -name __pycache__ -delete

# Downstream app: force-reinstall lib from ~/packages during lib iteration.
reallyclean:: clean
		rm -f pdm.lock
		pdm cache clear

# put `doc :: README.md` into Makefile, if desired
.PHONY:		README.md
README.md:
		pdm run python -m $(PROJECT) --md-help >$@

# vim: set ts=8 sw=8 noet:
