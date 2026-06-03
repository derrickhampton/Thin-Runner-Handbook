PYTHON := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: setup run smoke test

setup:
	/opt/homebrew/bin/python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -e .[dev]

run:
	$(PYTHON) -m orchestrator.cli --pipeline pipelines/hello_pipeline.yaml

smoke: run test

test:
	$(PYTHON) -m pytest -q