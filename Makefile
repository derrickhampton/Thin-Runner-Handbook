PYTHON := .venv/bin/python
PIP := .venv/bin/pip

.PHONY: setup run smoke test

setup:
	/opt/homebrew/bin/python3 -m venv .venv
	$(PIP) install --upgrade pip
	$(PIP) install -e .[dev]

run:
	.venv/bin/thin-runner run-skill hello_world --input skills/hello_world/input.example.json

smoke: run test

test:
	$(PYTHON) -m pytest -q