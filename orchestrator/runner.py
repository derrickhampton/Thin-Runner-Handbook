"""Pipeline runner implementation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .pipeline import load_pipeline


def run_pipeline(pipeline_path: Path, registry, memory_store, logger) -> dict[str, Any]:
    pipeline = load_pipeline(pipeline_path)
    steps_out: list[dict[str, Any]] = []

    for step in pipeline.get("steps", []):
        skill_name = step["skill"]
        payload = step.get("input", {})
        skill = registry.get(skill_name)

        logger.info("Running step '%s' with skill '%s'", step.get("name", skill_name), skill_name)
        output = skill(payload)

        record = {
            "step": step.get("name", skill_name),
            "skill": skill_name,
            "input": payload,
            "output": output,
        }
        steps_out.append(record)
        memory_store.append_run_record(record)

    run_summary = {"pipeline": pipeline.get("name", pipeline_path.stem), "steps": steps_out}
    memory_store.append_note(f"Completed pipeline: {run_summary['pipeline']}")
    return run_summary
