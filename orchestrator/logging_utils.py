"""Logging helpers for Thin Runner."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any


def create_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


class RunLogger:
    def __init__(self, log_dir: str | Path = "logs") -> None:
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def write_run_log(self, run_result: dict[str, Any]) -> Path:
        run_id = run_result.get("run_id", "unknown-run")
        path = self.log_dir / f"{run_id}.json"
        path.write_text(json.dumps(run_result, indent=2, ensure_ascii=True), encoding="utf-8")
        return path
