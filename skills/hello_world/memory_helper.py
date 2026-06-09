"""Idempotent daily top-3 memory writer.

Reads and updates a date-keyed section in memory/memory.md.
Running twice for the same date replaces the existing entry — no duplicates.
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_DATE_BLOCK_RE = re.compile(
    r"## Top 3: (\d{4}-\d{2}-\d{2})\n.*?(?=\n## |\Z)",
    re.DOTALL,
)


def update_daily_top3(
    top_posts: list[dict[str, Any]],
    date: str,
    topic: str,
    memory_path: str | Path = "memory/memory.md",
) -> None:
    """Write (or idempotently replace) the daily top-3 section for *date*.

    The file is created with a standard header if it does not already exist.
    An existing section for the same date is replaced, not appended.

    Args:
        top_posts: Ranked list of post dicts (rank, title, source, url, summary).
        date: ISO date string, e.g. ``"2026-06-08"``.
        topic: Search topic label.
        memory_path: Path to the memory markdown file.
    """
    path = Path(memory_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if not path.exists():
        path.write_text(
            "# Thin Runner Memory\n\n"
            "This file stores human-readable notes about Thin Runner executions.\n\n",
            encoding="utf-8",
        )

    existing = path.read_text(encoding="utf-8")
    timestamp = datetime.now(timezone.utc).isoformat()
    new_block = _build_block(top_posts=top_posts, date=date, topic=topic, timestamp=timestamp)

    # Match the specific date block only
    date_pattern = re.compile(
        rf"## Top 3: {re.escape(date)}\n.*?(?=\n## |\Z)",
        re.DOTALL,
    )

    if date_pattern.search(existing):
        updated = date_pattern.sub(new_block, existing)
    else:
        updated = existing.rstrip() + "\n\n" + new_block + "\n"

    path.write_text(updated, encoding="utf-8")


def _build_block(
    top_posts: list[dict[str, Any]],
    date: str,
    topic: str,
    timestamp: str,
) -> str:
    lines: list[str] = [
        f"## Top 3: {date}",
        f"Topic: `{topic}` | Updated: `{timestamp}`",
        "",
    ]
    for post in top_posts:
        rank = post.get("rank", "?")
        title = post.get("title", "")
        source = post.get("source", "")
        url = post.get("url", "")
        summary = post.get("summary", "")
        lines += [
            f"**{rank}. {title}**",
            f"- Source: {source}",
            f"- URL: {url}",
            f"- Summary: {summary}",
            "",
        ]
    return "\n".join(lines)
