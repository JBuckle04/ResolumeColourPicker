.PHONY: setup test run

PYTHON := .venv/bin/python
PIP := $(PYTHON) -m pip

pyproject.toml:
	touch pyproject.toml

.venv/pyvenv.cfg: 
	python3 -m venv .venv

.requirements-installed: pyproject.toml .venv/pyvenv.cfg
	$(PIP) install --upgrade pip
	$(PIP) install -e .
	touch .requirements-installed

setup: .requirements-installed

test: .requirements-installed
	$(PYTHON) -m unittest discover -s tests

run: .requirements-installed
	$(PYTHON) run.py