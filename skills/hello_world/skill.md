# Skill: hello_world

## Purpose
Return a predictable greeting from the Thin Runner system.

This skill proves that the runner can:
- load a skill by name
- pass JSON input to that skill
- receive structured JSON output
- write logs and memory after execution

## Inputs
JSON object:

```json
{
	"name": "Thin Runner"
}
```

## Outputs
JSON object:

```json
{
	"message": "Hello, Thin Runner!",
	"skill": "hello_world",
	"status": "success"
}
```

## Runtime
- Python 3.11+
- No external API keys
- No network access required

## Safety Rules
- Do not call external services.
- Do not read secrets.
- Do not mutate files outside memory/log handling performed by the orchestrator.

## Failure Modes
- Missing `name` should default to `Thin Runner`.
- Invalid JSON should be handled by the orchestrator before the skill is called.

## Observability
The orchestrator should record:
- skill name
- run ID
- input summary
- output summary
- status
- duration
- error, if any
