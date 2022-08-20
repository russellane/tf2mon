# tf2mon/Makefile

PROJECT		= tf2mon
SOURCES		= $(PROJECT) tests

build:		__pypackages__ tags lint test doc
		pdm build

__pypackages__:
		pdm install

.PHONY:		tags
tags:
		ctags -R --sort=no $(SOURCES) __pypackages__ 

lint:		black isort flake8

black:
		python -m black -q $(SOURCES)

isort:
		python -m isort $(SOURCES)

flake8:
		python -m flake8 $(SOURCES)

test:		pytest

pytest:
		python -m pytest --exitfirst --showlocals --verbose tests

pytest_debug:
		python -m pytest --exitfirst --showlocals --verbose --capture=no tests

doc:		README.md
.PHONY:		README.md
README.md:
		python -m $(PROJECT) --md-help >$@

clean:
		rm -rf .pytest_cache __pypackages__ dist tags
		find . -type f -name '*.py[co]' -delete
		find . -type d -name __pycache__ -delete

bump_micro:	_bump_micro clean build
_bump_micro:
		pdm bump micro

upload:
		twine upload --verbose -r pypi dist/*

.PHONY:		mypy
mypy:
		mypy $(PROJECT)

#-------------------------------------------------------------------------------

# ./.tf2 is a symlink to some .../SteamLibrary/steamapps/common/Team Fortress 2/tf/
CONLOG_FILE := .tf2/console.log
CONLOG_STAT := $(shell stat -c '%Y %s' $(CONLOG_FILE))
CONLOG_BKUP := conlogs/console.log-$(word 1, $(CONLOG_STAT))
CONLOG_SIZE := $(word 2, $(CONLOG_STAT))

rotate: $(CONLOG_BKUP)

$(CONLOG_BKUP): $(CONLOG_FILE)
	if [ $(CONLOG_SIZE) != 0 ]; then \
		mv $< $@ ;\
		chmod 644 $@ ;\
		ln -sf $@ latest ;\
		ls -lh $@ latest ;\
		cp /dev/null $< ;\
	else \
		echo not rotating empty logfile ;\
	fi ;\
	ls -lh $<

cleanlog:	latest
		python -m tf2mon --clean-con-logfile latest >$@

distclean::
	rm -f cleanlog latest

uml:
	pdm run pyreverse -ASmy tf2mon ../libcli ../libcurses
	dot -Tpdf classes.dot -o output.pdf
	xdg-open output.pdf

#-------------------------------------------------------------------------------
# vim: set ts=8 sw=8 noet:
