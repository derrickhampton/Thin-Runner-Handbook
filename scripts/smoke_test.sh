#!/usr/bin/env bash
set -euo pipefail

python -m pytest
thin-runner run-skill hello_world --json '{"name":"Smoke Test"}'
thin-runner run-pipeline pipelines/hello_pipeline.yaml

echo "Thin Runner smoke test passed."
