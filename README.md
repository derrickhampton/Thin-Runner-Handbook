# Thin Runner Handbook

A small, transparent workflow executor for running predefined skills and
pipelines with explicit inputs, visible outputs, logs, and file-based memory.

Website: [ThinRunner.com](https://ThinRunner.com)

## What is a Thin Runner?

A Thin Runner runs the right skill at the right time with the right inputs,
then records what happened.

It is not a heavyweight autonomous agent. It does not keep a hidden reasoning
loop running in the background. It is intentionally boring: load config, run a
skill or pipeline, capture output, write memory, write logs.

## Base Flow

```text
CLI / cron / webhook / GitHub Action
|
v
Thin Runner orchestrator
|
v
Skill or pipeline
|
v
Structured output
|
v
Memory + logs
```

## Quickstart

```bash
git clone https://github.com/derrickhampton/Thin-Runner-Handbook.git
cd Thin-Runner-Handbook
bash scripts/setup_dev.sh
source .venv/bin/activate
```

## Run the hello-world skill

```bash
thin-runner run-skill hello_world --json '{"name":"Thin Runner"}'
```

## Run the hello pipeline

```bash
thin-runner run-pipeline pipelines/hello_pipeline.yaml
```

## Inspect outputs

```bash
cat memory/runs.jsonl
tail -n 40 memory/memory.md
ls logs/
```

## Run the local dashboard

Install API dependencies and start the dashboard backend:

```bash
python -m pip install -e ".[dev,api]"
uvicorn api.main:app --reload --host 127.0.0.1 --port 8787
```

Open <http://127.0.0.1:8787> in your browser.

Dashboard features in this first version:

- list registered skills from `config/skills.example.yaml`
- execute a selected skill with JSON input
- view latest runs from `memory/runs.jsonl`
- open structured run logs from `logs/<run_id>.json`
- read `memory/memory.md`
- read/update a Thin Runner-managed cron block with command and schedule validation

## Core Components

| Path | Purpose |
| --- | --- |
| orchestrator/ | Thin Runner execution layer |
| skills/ | Focused executable units |
| pipelines/ | Ordered skill workflows |
| memory/ | Human and machine-readable run history |
| logs/ | Per-run structured JSON logs |
| config/ | Explicit skill and runner configuration |
| .github/workflows/ | CI smoke checks |

## Extra setup notes

If your system does not already include Python 3.11+ and `venv`, install them first.
For Ubuntu:

```bash
sudo apt update
sudo apt install -y python3 python3-venv
```

## Philosophy

Put the workflow in the center, not the agent.
