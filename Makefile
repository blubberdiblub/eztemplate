# useful actions

PROJECT := eztemplate
TESTS := tests
VENV := venv

ACTIVATE := . $(VENV)/bin/activate
FIND := /usr/bin/find
RM := /bin/rm
SETUP := ./setup.py
VIRTUALENV := /usr/bin/virtualenv

.PHONY: clean
clean:
	$(SETUP) clean --all
	$(RM) -rf -- $(PROJECT).egg-info
	$(FIND) $(PROJECT) $(TESTS) -type f -name '*.pyc' -delete
	$(FIND) $(PROJECT) $(TESTS) -depth -type d -name '__pycache__' -delete

.PHONY: cleanvenv
cleanvenv:
	$(RM) -rf -- $(VENV)

$(VENV):
	$(VIRTUALENV) $(VENV)

.PHONY: empy
empy: $(VENV)
	$(ACTIVATE) && pip install empy

.PHONY: mako
mako: $(VENV)
	$(ACTIVATE) && pip install mako

.PHONY: install
install: $(VENV)
	$(ACTIVATE) && pip install --upgrade --force-reinstall .

.PHONY: test
test:
	$(SETUP) test

.PHONY: sdist
sdist:
	$(SETUP) sdist

.PHONY: bdist
bdist:
	$(SETUP) bdist

.PHONY: wheel
wheel:
	$(SETUP) bdist_wheel

.PHONY: dists
dists: sdist bdist wheel
