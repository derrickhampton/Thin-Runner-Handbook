from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class RunService:
    def __init__(self, runs_path: str = "memory/runs.jsonl", logs_dir: str = "logs") -> None:
        self.runs_path = Path(runs_path)
        self.logs_dir = Path(logs_dir)

    def list_runs(self, limit: int = 25) -> list[dict[str, Any]]:
        if not self.runs_path.exists():
            return []

        lines = self.runs_path.read_text(encoding="utf-8").splitlines()
        parsed: list[dict[str, Any]] = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            parsed.append(json.loads(line))

        parsed.reverse()
        return parsed[:limit]

    def get_run_log(self, run_id: str) -> dict[str, Any]:
        path = self.logs_dir / f"{run_id}.json"
        if not path.exists():
            raise FileNotFoundError(f"Run log not found: {path}")
        return json.loads(path.read_text(encoding="utf-8"))
