"""Ollama local-inference helper.

Reads OLLAMA_BASE_URL and OLLAMA_MODEL from the environment.
Sends posts to a local Ollama model for relevance ranking and summarisation.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

OLLAMA_DEFAULT_URL = "http://localhost:11434"
OLLAMA_DEFAULT_MODEL = "llama3"


def get_config(
    model: str | None = None,
    base_url: str | None = None,
) -> tuple[str, str]:
    """Return (model, base_url), reading from env when not provided explicitly."""
    resolved_model = model or os.environ.get("OLLAMA_MODEL", OLLAMA_DEFAULT_MODEL)
    resolved_url = base_url or os.environ.get("OLLAMA_BASE_URL", OLLAMA_DEFAULT_URL)
    return resolved_model, resolved_url.rstrip("/")


def rank_and_summarize(
    posts: list[dict[str, Any]],
    count: int = 3,
    model: str | None = None,
    base_url: str | None = None,
) -> list[dict[str, Any]]:
    """Ask Ollama to rank *posts* and return the top *count* with summaries.

    Args:
        posts: Raw posts from Brave (title, source, url, description).
        count: Number of top posts to return.
        model: Override for OLLAMA_MODEL env var.
        base_url: Override for OLLAMA_BASE_URL env var.

    Returns:
        List of dicts: rank, title, source, url, summary.

    Raises:
        RuntimeError: When Ollama is unreachable or returns a malformed response.
    """
    resolved_model, resolved_url = get_config(model=model, base_url=base_url)

    posts_text = "\n".join(
        f"{i + 1}. {p['title']}\n"
        f"   Source: {p['source']}\n"
        f"   URL:    {p['url']}\n"
        f"   Desc:   {p.get('description', '')}"
        for i, p in enumerate(posts)
    )

    prompt = (
        f"You are a news relevance assistant. "
        f"Given the following {len(posts)} social news items, "
        f"select the top {count} most relevant and interesting posts.\n\n"
        f"Return ONLY a valid JSON array (no markdown, no extra text) "
        f"where each element has these keys:\n"
        f"  rank    (integer 1–{count})\n"
        f"  title   (string, original title)\n"
        f"  source  (string)\n"
        f"  url     (string)\n"
        f"  summary (1–2 sentence summary)\n\n"
        f"Posts:\n{posts_text}\n"
    )

    payload = json.dumps(
        {"model": resolved_model, "prompt": prompt, "stream": False}
    ).encode()

    req = urllib.request.Request(
        f"{resolved_url}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            data: dict[str, Any] = json.loads(response.read())
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Could not reach Ollama at {resolved_url}. "
            f"Is it running? Error: {exc.reason}"
        ) from exc

    raw_response: str = data.get("response", "")
    # Extract the JSON array from any surrounding text
    start = raw_response.find("[")
    end = raw_response.rfind("]") + 1
    if start == -1 or end == 0:
        raise RuntimeError(
            f"Ollama did not return a valid JSON array. "
            f"Response: {raw_response[:300]}"
        )

    ranked: list[dict[str, Any]] = json.loads(raw_response[start:end])
    return ranked[:count]
