PROJECT = tf2mon
include Python.mk
doc :: README.md

MYPYOPTS +=	--disallow-any-generics
MYPYOPTS +=	--disallow-untyped-defs
lint::		mypy

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
