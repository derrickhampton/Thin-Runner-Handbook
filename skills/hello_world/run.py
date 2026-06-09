"""Social news skill.

Fetches top social news posts via Brave Search, ranks and summarises them
with a local Ollama model, then writes the daily top-3 to memory.md.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from skills.hello_world.brave_helper import fetch_news_posts
from skills.hello_world.memory_helper import update_daily_top3
from skills.hello_world.ollama_helper import rank_and_summarize


def run(input_data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Fetch, rank, and remember the daily top-3 social news posts.

    Input keys:
        topic       (str)  – search query, default "social news"
        date        (str)  – ISO date YYYY-MM-DD, default today UTC
        limit       (int)  – max Brave results to fetch, default 10
        memory_path (str)  – override for memory.md path (mainly for testing)

    Returns a dict matching the skill output contract.
    """
    input_data = input_data or {}
    topic = str(input_data.get("topic") or "social news").strip() or "social news"
    date = str(input_data.get("date") or datetime.now(timezone.utc).date()).strip()
    limit = int(input_data.get("limit") or 10)
    memory_path = input_data.get("memory_path", "memory/memory.md")

    # --- Brave fetch ---
    try:
        posts = fetch_news_posts(topic=topic, limit=limit)
    except ValueError as exc:
        # Missing API key — controlled failure
        return _error(str(exc), date)
    except Exception as exc:
        return _error(f"Brave fetch failed: {exc}", date)

    if not posts:
        return _error("Brave returned no results for this topic", date)

    # --- Ollama ranking ---
    try:
        top_posts = rank_and_summarize(posts=posts, count=3)
    except Exception as exc:
        return _error(f"Ollama ranking failed: {exc}", date)

    # --- Memory write (idempotent) ---
    update_daily_top3(
        top_posts=top_posts,
        date=date,
        topic=topic,
        memory_path=memory_path,
    )

    return {
        "skill": "hello_world",
        "status": "success",
        "date": date,
        "top_posts": top_posts,
        "message": f"Tracked top 3 social news posts for {date}",
    }


def _error(reason: str, date: str) -> dict[str, Any]:
    return {
        "skill": "hello_world",
        "status": "failed",
        "date": date,
        "top_posts": [],
        "message": reason,
    }
