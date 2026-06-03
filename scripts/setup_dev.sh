#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"

echo "Development environment ready."
echo "Run: source .venv/bin/activate"
echo "Then: thin-runner --help"
