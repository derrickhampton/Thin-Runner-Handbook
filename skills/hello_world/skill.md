# Skill: hello_world

## Purpose

Fetch the daily top-3 social news posts via Brave Search, rank and summarise
them with a local Ollama model, and write the results to `memory/memory.md`.

## Inputs

JSON object:

```json
{
  "topic": "social news",
  "date": "YYYY-MM-DD",
  "limit": 10
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| topic | string | `"social news"` | Brave Search query |
| date | string | today UTC | ISO date key for memory entry |
| limit | integer | `10` | Max Brave results to fetch (capped at 20) |
| memory_path | string | `"memory/memory.md"` | Override for tests |

## Outputs

JSON object:

```json
{
  "skill": "hello_world",
  "status": "success",
  "date": "2026-06-08",
  "top_posts": [
    {
      "rank": 1,
      "title": "...",
      "source": "...",
      "url": "...",
      "summary": "..."
    }
  ],
  "message": "Tracked top 3 social news posts for 2026-06-08"
}
```

`status` is `"failed"` and `top_posts` is `[]` when Brave or Ollama are unavailable.

## Runtime

- Python 3.11+
- Brave Search API key (`BRAVE_API_KEY` in env)
- Ollama running locally (`OLLAMA_BASE_URL`, `OLLAMA_MODEL` in env)

## Config

Set in `.env` (see `.env.example`):

```
BRAVE_API_KEY=your-key-here
BRAVE_API_URL=https://api.search.brave.com/res/v1/news/search  # optional override
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

## Helpers

| File | Purpose |
|---|---|
| `brave_helper.py` | Brave API key management and HTTP fetch |
| `ollama_helper.py` | Ollama prompt construction and JSON parsing |
| `memory_helper.py` | Idempotent daily top-3 writer for `memory.md` |

## Safety Rules

- API key is read from environment only — never hardcoded.
- Does not write outside `memory/memory.md` and orchestrator-managed files.
- Returns a controlled `failed` status when upstream services are unavailable.

## Failure Modes

| Condition | Behaviour |
|---|---|
| `BRAVE_API_KEY` not set | Returns `status: failed` with a clear message |
| Brave returns no results | Returns `status: failed` |
| Brave HTTP error | Returns `status: failed` with HTTP status |
| Ollama unreachable | Returns `status: failed` with connection error |
| Ollama returns malformed JSON | Returns `status: failed` with parse error |

## Memory Behaviour

Running twice for the same `date` replaces the existing `## Top 3: YYYY-MM-DD`
block — no duplicate entries are written.

## Observability

The orchestrator records: skill name, run ID, input, output, status, duration,
and any error string.
