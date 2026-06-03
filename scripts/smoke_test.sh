#!/usr/bin/env bash
set -euo pipefail

thin-runner run-skill hello_world --input skills/hello_world/input.example.json
pytest -q
