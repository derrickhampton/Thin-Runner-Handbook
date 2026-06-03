"""File-backed memory stores for Thin Runner execution history."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class MemoryStore:
    def __init__(
        self,
        jsonl_path: str | Path = "memory/runs.jsonl",
        markdown_path: str | Path = "memory/memory.md",
    ) -> None:
        self.jsonl_path = Path(jsonl_path)
        self.markdown_path = Path(markdown_path)
        self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        self.markdown_path.parent.mkdir(parents=True, exist_ok=True)
        self.jsonl_path.touch(exist_ok=True)
        self._ensure_markdown_file()

    def append_run(self, run_result: dict[str, Any]) -> None:
        with self.jsonl_path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(run_result, ensure_ascii=True) + "\n")

        self._append_markdown_summary(run_result)

    def _ensure_markdown_file(self) -> None:
        if self.markdown_path.exists():
            return
        self.markdown_path.write_text(
            "# Thin Runner Memory\n\n"
            "This file stores human-readable notes about Thin Runner executions.\n\n"
            "## Recent Runs\n\n"
            "No runs recorded yet.\n",
            encoding="utf-8",
        )

    def _append_markdown_summary(self, run_result: dict[str, Any]) -> None:
        existing = self.markdown_path.read_text(encoding="utf-8")
        if "No runs recorded yet." in existing:
            existing = existing.replace("No runs recorded yet.\n", "")
            self.markdown_path.write_text(existing, encoding="utf-8")

        summary = [
            "\n---\n",
            f"## Run {run_result.get('run_id')}\n",
            f"- Skill: `{run_result.get('skill')}`\n",
            f"- Status: `{run_result.get('status')}`\n",
            f"- Started: `{run_result.get('started_at')}`\n",
            f"- Duration: `{run_result.get('duration_ms')}ms`\n",
        ]

        if run_result.get("error"):
            summary.append(f"- Error: `{run_result.get('error')}`\n")

        with self.markdown_path.open("a", encoding="utf-8") as file:
            file.writelines(summary)


class FileMemoryStore:
    def __init__(self, memory_file: Path, runs_file: Path):
        self.memory_file = memory_file
        self.runs_file = runs_file
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        self.runs_file.parent.mkdir(parents=True, exist_ok=True)
        self.memory_file.touch(exist_ok=True)
        self.runs_file.touch(exist_ok=True)

    def append_note(self, note: str) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        with self.memory_file.open("a", encoding="utf-8") as f:
            f.write(f"- {timestamp} {note}\n")

    def append_run_record(self, record: dict) -> None:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **record,
        }
        with self.runs_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=True) + "\n")
