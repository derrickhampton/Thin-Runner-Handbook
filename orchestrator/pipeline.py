"""Pipeline parsing and execution helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any, TYPE_CHECKING

import yaml

if TYPE_CHECKING:
    from orchestrator.runner import ThinRunner


def load_pipeline(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    if "steps" not in data:
        raise ValueError(f"Pipeline at {path} is missing required 'steps' key")
    return data


class PipelineRunner:
    def __init__(self, runner: "ThinRunner" | None = None) -> None:
        if runner is None:
            from orchestrator.runner import ThinRunner

            self.runner = ThinRunner()
        else:
            self.runner = runner

    def run_pipeline(self, pipeline_path: str | Path) -> dict[str, Any]:
        path = Path(pipeline_path)
        data = load_pipeline(path)
        steps = data.get("steps", [])

        results: list[dict[str, Any]] = []
        status = "success"

        for step in steps:
            skill_name = step["skill"]
            input_data = step.get("input", {})
            result = self.runner.run_skill(skill_name, input_data).to_dict()
            result["step_name"] = step.get("name", skill_name)
            results.append(result)

            if result["status"] != "success":
                status = "failed"
                break

        return {
            "pipeline": data.get("name", path.stem),
            "status": status,
            "steps": results,
        }
