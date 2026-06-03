#!/usr/bin/env bash
set -euo pipefail

python -m orchestrator.cli --pipeline pipelines/hello_pipeline.yaml
pytest -q
