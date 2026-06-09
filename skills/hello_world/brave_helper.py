"""Brave Search API helper.

The API key is read from the environment (BRAVE_API_KEY).
Override the endpoint with BRAVE_API_URL if needed.
"""

from __future__ import annotations

import gzip
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

BRAVE_DEFAULT_URL = "https://api.search.brave.com/res/v1/news/search"


def get_config(
    api_key: str | None = None,
    api_url: str | None = None,
) -> tuple[str, str]:
    """Return (api_key, api_url), reading from env when not provided explicitly."""
    resolved_key = api_key or os.environ.get("BRAVE_API_KEY", "")
    resolved_url = api_url or os.environ.get("BRAVE_API_URL", BRAVE_DEFAULT_URL)

    if not resolved_key:
        raise ValueError(
            "BRAVE_API_KEY is not set. "
            "Add it to your .env file or set it in the environment."
        )

    return resolved_key, resolved_url


def fetch_news_posts(
    topic: str,
    limit: int = 10,
    api_key: str | None = None,
    api_url: str | None = None,
) -> list[dict[str, Any]]:
    """Fetch candidate news posts from Brave Search for *topic*.

    Args:
        topic: Search query string.
        limit: Maximum number of results to return (capped at 20 by Brave).
        api_key: Override for BRAVE_API_KEY env var.
        api_url: Override for BRAVE_API_URL env var.

    Returns:
        List of dicts with keys: title, source, url, description.

    Raises:
        ValueError: When BRAVE_API_KEY is missing.
        urllib.error.HTTPError: On 4xx/5xx responses.
        RuntimeError: On unexpected upstream errors.
    """
    key, url = get_config(api_key=api_key, api_url=api_url)

    params = urllib.parse.urlencode({"q": topic, "count": min(limit, 20)})
    full_url = f"{url}?{params}"

    req = urllib.request.Request(
        full_url,
        headers={
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": key,
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            raw = response.read()
            encoding = response.headers.get("Content-Encoding", "")
            if encoding == "gzip":
                raw = gzip.decompress(raw)
            data: dict[str, Any] = json.loads(raw)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Brave API returned HTTP {exc.code}: {exc.reason}") from exc

    results = data.get("results", [])
    posts: list[dict[str, Any]] = []
    for item in results[:limit]:
        posts.append(
            {
                "title": item.get("title", ""),
                "source": item.get("source", item.get("url", "")),
                "url": item.get("url", ""),
                "description": item.get("description", ""),
            }
        )
    return posts
