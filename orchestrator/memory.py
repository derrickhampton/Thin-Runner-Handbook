"""Simple file-backed memory for notes and run history."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path


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
