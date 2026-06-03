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

1. macOS setup:

```bash
./scripts/setup_dev.sh
source .venv/bin/activate
```

1. Ubuntu setup:

```bash
sudo apt update
sudo apt install -y python3 python3-venv
./scripts/setup_dev.sh
source .venv/bin/activate
```

1. Verify the CLI entrypoint:

```bash
thin-runner --help
```

1. Run tests:

```bash
pytest -q
```

1. Optional Makefile workflow:

```bash
make setup
make test
make smoke
```

## Repository layout

- `orchestrator/` contains the thin runner core.
- `skills/` contains skill implementations.
- `pipelines/` contains YAML pipelines.
- `memory/` tracks notes and run history.
- `logs/` and `runs/` hold runtime outputs.
- `tests/` contains baseline tests.
