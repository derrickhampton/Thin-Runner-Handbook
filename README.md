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

1. Create the local development environment:

```bash
make setup
```

1. Run tests:

```bash
make test
```

1. Run the smoke flow (pipeline + tests):

```bash
make smoke
```

## Repository layout

- `orchestrator/` contains the thin runner core.
- `skills/` contains skill implementations.
- `pipelines/` contains YAML pipelines.
- `memory/` tracks notes and run history.
- `logs/` and `runs/` hold runtime outputs.
- `tests/` contains baseline tests.
