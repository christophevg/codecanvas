APP=codecanvas

PYTHON=PYTHONPATH=src/:lib/py-util/src:. python
COVERAGE=/usr/local/bin/coverage

all: test

test:
	@echo "*** performing $(APP) tests"
	@$(PYTHON) $(COVERAGE) run test/all.py

.PHONY: test
