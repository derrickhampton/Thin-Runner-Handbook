"""Pipeline parsing helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def load_pipeline(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if "steps" not in data:
        raise ValueError(f"Pipeline at {path} is missing required 'steps' key")
    return data
