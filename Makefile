APP=codecanvas

PYTHON=PYTHONPATH=src/:lib/py-util/src:. /opt/local/bin/python2.7
COVERAGE=/opt/local/bin/coverage-2.7

all: test

test:
	@echo "*** performing $(APP) tests"
	@$(PYTHON) $(COVERAGE) run test/all.py

.PHONY: test
