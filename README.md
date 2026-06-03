# Thin Runner Handbook

A small, transparent workflow executor for running predefined skills and
pipelines with explicit inputs, visible outputs, logs, and file-based memory.

Website: https://ThinRunner.com

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
