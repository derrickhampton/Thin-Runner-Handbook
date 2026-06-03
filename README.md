# Thin Runner Handbook

This repository is the base Thin Runner model for the Thin Runner Handbook.

The goal is to keep the workflow visible and inspectable:

- small, file-based skills
- explicit pipeline orchestration
- simple local memory
- observable run logs

This first version is intentionally minimal. It is a working scaffold you can clone,
inspect, and run without hidden setup steps.

## Quick start

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -e .[dev]
```

1. Run a smoke test:

```bash
./scripts/smoke_test.sh
```

## Repository layout

- `orchestrator/` contains the thin runner core.
- `skills/` contains skill implementations.
- `pipelines/` contains YAML pipelines.
- `memory/` tracks notes and run history.
- `logs/` and `runs/` hold runtime outputs.
- `tests/` contains baseline tests.
