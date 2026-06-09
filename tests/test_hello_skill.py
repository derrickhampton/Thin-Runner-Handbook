"""Tests for the hello_world social-news skill and its helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

# ---------------------------------------------------------------------------
# Fixtures / helpers
# ---------------------------------------------------------------------------

_BRAVE_POSTS = [
    {
        "title": f"Post {i}",
        "source": f"source{i}.com",
        "url": f"https://source{i}.com/article",
        "description": f"Description {i}",
    }
    for i in range(1, 6)
]

_TOP_POSTS = [
    {"rank": 1, "title": "Post 1", "source": "source1.com", "url": "https://source1.com/article", "summary": "Summary 1."},
    {"rank": 2, "title": "Post 2", "source": "source2.com", "url": "https://source2.com/article", "summary": "Summary 2."},
    {"rank": 3, "title": "Post 3", "source": "source3.com", "url": "https://source3.com/article", "summary": "Summary 3."},
]


# ---------------------------------------------------------------------------
# brave_helper unit tests
# ---------------------------------------------------------------------------

class TestBraveHelper:
    def test_get_config_raises_when_key_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("BRAVE_API_KEY", raising=False)
        from skills.hello_world import brave_helper

        with pytest.raises(ValueError, match="BRAVE_API_KEY is not set"):
            brave_helper.get_config()

    def test_get_config_reads_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BRAVE_API_KEY", "test-key")
        monkeypatch.setenv("BRAVE_API_URL", "https://custom.example.com/search")
        from skills.hello_world import brave_helper

        key, url = brave_helper.get_config()
        assert key == "test-key"
        assert url == "https://custom.example.com/search"

    def test_get_config_explicit_args_override_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BRAVE_API_KEY", "env-key")
        from skills.hello_world import brave_helper

        key, url = brave_helper.get_config(api_key="explicit-key", api_url="https://override.com")
        assert key == "explicit-key"
        assert url == "https://override.com"


# ---------------------------------------------------------------------------
# ollama_helper unit tests
# ---------------------------------------------------------------------------

class TestOllamaHelper:
    def test_get_config_defaults(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("OLLAMA_MODEL", raising=False)
        monkeypatch.delenv("OLLAMA_BASE_URL", raising=False)
        from skills.hello_world import ollama_helper

        model, url = ollama_helper.get_config()
        assert model == "llama3"
        assert url == "http://localhost:11434"

    def test_get_config_reads_from_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OLLAMA_MODEL", "mistral")
        monkeypatch.setenv("OLLAMA_BASE_URL", "http://192.168.1.10:11434")
        from skills.hello_world import ollama_helper

        model, url = ollama_helper.get_config()
        assert model == "mistral"
        assert url == "http://192.168.1.10:11434"


# ---------------------------------------------------------------------------
# memory_helper unit tests
# ---------------------------------------------------------------------------

class TestMemoryHelper:
    def test_creates_file_and_writes_block(self, tmp_path: Path) -> None:
        from skills.hello_world.memory_helper import update_daily_top3

        memory_file = tmp_path / "memory.md"
        update_daily_top3(_TOP_POSTS, date="2026-06-08", topic="tech news", memory_path=memory_file)

        content = memory_file.read_text()
        assert "## Top 3: 2026-06-08" in content
        assert "Post 1" in content
        assert "Summary 1." in content

    def test_same_date_replaces_not_duplicates(self, tmp_path: Path) -> None:
        from skills.hello_world.memory_helper import update_daily_top3

        memory_file = tmp_path / "memory.md"
        update_daily_top3(_TOP_POSTS, date="2026-06-08", topic="news", memory_path=memory_file)

        updated_posts = [
            {"rank": 1, "title": "Updated Post", "source": "new.com", "url": "https://new.com", "summary": "New summary."},
            *_TOP_POSTS[1:],
        ]
        update_daily_top3(updated_posts, date="2026-06-08", topic="news", memory_path=memory_file)

        content = memory_file.read_text()
        assert content.count("## Top 3: 2026-06-08") == 1, "Should not duplicate the date block"
        assert "Updated Post" in content
        assert "Post 1" not in content  # original first post should be gone

    def test_different_dates_coexist(self, tmp_path: Path) -> None:
        from skills.hello_world.memory_helper import update_daily_top3

        memory_file = tmp_path / "memory.md"
        update_daily_top3(_TOP_POSTS, date="2026-06-07", topic="news", memory_path=memory_file)
        update_daily_top3(_TOP_POSTS, date="2026-06-08", topic="news", memory_path=memory_file)

        content = memory_file.read_text()
        assert "## Top 3: 2026-06-07" in content
        assert "## Top 3: 2026-06-08" in content


# ---------------------------------------------------------------------------
# run() integration tests (helpers fully mocked)
# ---------------------------------------------------------------------------

class TestRun:
    def test_success_path(self, tmp_path: Path) -> None:
        from skills.hello_world.run import run

        with (
            patch("skills.hello_world.run.fetch_news_posts", return_value=_BRAVE_POSTS),
            patch("skills.hello_world.run.rank_and_summarize", return_value=_TOP_POSTS),
        ):
            result = run({"topic": "tech", "date": "2026-06-08", "memory_path": str(tmp_path / "memory.md")})

        assert result["status"] == "success"
        assert result["skill"] == "hello_world"
        assert result["date"] == "2026-06-08"
        assert len(result["top_posts"]) == 3
        assert "2026-06-08" in result["message"]

    def test_missing_api_key_returns_failed(self) -> None:
        from skills.hello_world.run import run

        with patch(
            "skills.hello_world.run.fetch_news_posts",
            side_effect=ValueError("BRAVE_API_KEY is not set."),
        ):
            result = run({"date": "2026-06-08"})

        assert result["status"] == "failed"
        assert "BRAVE_API_KEY" in result["message"]
        assert result["top_posts"] == []

    def test_brave_upstream_failure_returns_failed(self) -> None:
        from skills.hello_world.run import run

        with patch(
            "skills.hello_world.run.fetch_news_posts",
            side_effect=RuntimeError("Brave API returned HTTP 429: Too Many Requests"),
        ):
            result = run({"date": "2026-06-08"})

        assert result["status"] == "failed"
        assert "Brave fetch failed" in result["message"]

    def test_brave_empty_results_returns_failed(self) -> None:
        from skills.hello_world.run import run

        with patch("skills.hello_world.run.fetch_news_posts", return_value=[]):
            result = run({"date": "2026-06-08"})

        assert result["status"] == "failed"
        assert "no results" in result["message"].lower()

    def test_ollama_failure_returns_failed(self) -> None:
        from skills.hello_world.run import run

        with (
            patch("skills.hello_world.run.fetch_news_posts", return_value=_BRAVE_POSTS),
            patch(
                "skills.hello_world.run.rank_and_summarize",
                side_effect=RuntimeError("Could not reach Ollama at http://localhost:11434"),
            ),
        ):
            result = run({"date": "2026-06-08"})

        assert result["status"] == "failed"
        assert "Ollama ranking failed" in result["message"]

    def test_idempotent_same_day_memory_update(self, tmp_path: Path) -> None:
        from skills.hello_world.run import run

        memory_file = tmp_path / "memory.md"

        first_posts = [
            {"rank": 1, "title": "First", "source": "a.com", "url": "https://a.com", "summary": "First run."},
            *_TOP_POSTS[1:],
        ]
        second_posts = [
            {"rank": 1, "title": "Second", "source": "b.com", "url": "https://b.com", "summary": "Second run."},
            *_TOP_POSTS[1:],
        ]

        with (
            patch("skills.hello_world.run.fetch_news_posts", return_value=_BRAVE_POSTS),
            patch("skills.hello_world.run.rank_and_summarize", return_value=first_posts),
        ):
            run({"date": "2026-06-08", "memory_path": str(memory_file)})

        with (
            patch("skills.hello_world.run.fetch_news_posts", return_value=_BRAVE_POSTS),
            patch("skills.hello_world.run.rank_and_summarize", return_value=second_posts),
        ):
            run({"date": "2026-06-08", "memory_path": str(memory_file)})

        content = memory_file.read_text()
        assert content.count("## Top 3: 2026-06-08") == 1
        assert "Second" in content
        assert "First" not in content

