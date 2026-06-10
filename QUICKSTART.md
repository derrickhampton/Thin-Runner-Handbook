# Thin Runner Handbook Quickstart

This guide gets you from clone to first successful runs with explicit input, visible output, structured logs, and file-based memory.

## What You Will Build / Run

By the end of this quickstart, you will:

- run the local-first Thin Runner CLI
- execute the `hello_world` skill with explicit JSON input
- execute the `hello_pipeline` pipeline
- inspect file-based memory and structured run logs
- run tests to verify the repo state
- optionally start the API/dashboard backend

## Requirements

- macOS, Linux, or WSL
- Python 3.11+
- Git
- terminal with `bash`/`zsh`

Check Python version:

```bash
python3 --version
```

## Clone the Repository

```bash
git clone https://github.com/derrickhampton/Thin-Runner-Handbook.git
cd Thin-Runner-Handbook
```

## Set Up the Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

When activated, your shell prompt usually shows `(.venv)`.

## Install Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Why editable mode: changes in this repo are picked up immediately without reinstalling.

## Run the Hello World Skill

Run a single small skill with explicit input:

```bash
thin-runner run-skill hello_world --json '{"name":"Thin Runner"}'
```

Expected result: a visible command result in your terminal, plus a new run entry in memory and a new JSON log file.

## Run the Hello Pipeline

Run a clear, file-defined pipeline:

```bash
thin-runner run-pipeline pipelines/hello_pipeline.yaml
```

Expected result: predictable execution steps, visible output, and another recorded run.

## Inspect Memory

Thin Runner keeps memory in files so execution history is inspectable.

```bash
cat memory/runs.jsonl
tail -n 40 memory/memory.md
```

What to look for:

- `memory/runs.jsonl`: append-only run records
- `memory/memory.md`: human-readable notes/history

## Inspect Logs

Logs are structured JSON files, one file per run.

```bash
ls logs/
```

Open one log file (replace with an actual filename from `ls`):

```bash
cat logs/<run_id>.json
```

If you want a quick one-liner:

```bash
cat "logs/$(ls logs | head -n 1)"
```

## Run Tests

```bash
python -m pytest
```

This validates orchestrator behavior, pipeline behavior, and sample skill behavior.

## Optional: Start the Dashboard

This repository includes `api/` and `ui/`, so you can start the API/dashboard backend locally.

Install API extras and run the server:

```bash
python -m pip install -e ".[dev,api]"
uvicorn api.main:app --reload --host 127.0.0.1 --port 8787
```

Open:

```text
http://127.0.0.1:8787
```

## Project Structure

- `orchestrator/`: CLI and execution engine that runs skills/pipelines and writes outputs.
- `skills/`: small, focused executable units (like `hello_world`).
- `pipelines/`: YAML-defined ordered workflows that call one or more skills.
- `memory/`: file-based memory (`runs.jsonl`, `memory.md`) for persistent, inspectable state.
- `logs/`: structured per-run JSON logs for debugging and auditability.
- `runs/`: run artifacts and generated execution outputs.
- `config/`: example runner/skill configuration files.
- `tests/`: pytest suite for orchestrator, pipelines, services, and skills.
- `.github/workflows/`: CI workflows for repeatable checks in automation.
- `api/`: FastAPI backend endpoints for runs, memory, skills, and cron operations.
- `ui/`: frontend assets for the local dashboard experience.

## Troubleshooting

- `thin-runner: command not found`
  - Confirm venv is active: `source .venv/bin/activate`
  - Reinstall package entry points: `python -m pip install -e ".[dev]"`
  - Verify script location: `python -m pip show thin-runner-handbook`

- virtual environment not activated
  - Activate from repo root: `source .venv/bin/activate`
  - If `.venv` does not exist, create it again: `python3 -m venv .venv`

- missing dependencies
  - Re-run install: `python -m pip install -e ".[dev]"`
  - For dashboard/API: `python -m pip install -e ".[dev,api]"`

- no logs created yet
  - Run a skill or pipeline first.
  - Then confirm files: `ls logs/`

- empty memory files
  - Run at least one command:
    - `thin-runner run-skill hello_world --json '{"name":"Thin Runner"}'`
  - Re-check memory:
    - `cat memory/runs.jsonl`
    - `tail -n 40 memory/memory.md`

- pipeline file not found
  - Verify path from repo root: `ls pipelines/`
  - Run with explicit path: `thin-runner run-pipeline pipelines/hello_pipeline.yaml`

- dashboard not starting
  - Confirm API deps installed: `python -m pip install -e ".[dev,api]"`
  - Confirm port is free or change port:
    - `uvicorn api.main:app --reload --host 127.0.0.1 --port 8788`

- invalid JSON input
  - Use valid JSON with double quotes inside single-quoted shell string:
    - `thin-runner run-skill hello_world --json '{"name":"Thin Runner"}'`
  - Validate quickly:
    - `python -m json.tool <<< '{"name":"Thin Runner"}'`

## Next Steps

1. Add a second skill under `skills/` with explicit input/output.
2. Compose a multi-step pipeline in `pipelines/`.
3. Add tests in `tests/` for your new skill and pipeline.
4. Wire scheduled or API-triggered execution via `api/` routes.
5. Keep memory and logs visible during development for predictable execution.