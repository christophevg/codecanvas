PYTHON=PYTHONPATH=src/:. /opt/local/bin/python2.7
COVERAGE=/opt/local/bin/coverage-2.7

all: test

test:
	@echo "*** performing tests"
	@$(PYTHON) $(COVERAGE) run test/all.py

.PHONY: test
