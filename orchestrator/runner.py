"""Thin Runner core orchestration and pipeline compatibility helpers."""

from __future__ import annotations

import time
import traceback
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from .memory import MemoryStore
from .pipeline import load_pipeline
from .registry import SkillRegistry


@dataclass
class RunResult:
    run_id: str
    skill: str
    status: str
    started_at: str
    duration_ms: int
    input: dict[str, Any]
    output: dict[str, Any] | None = None
    error: str | None = None
    traceback: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ThinRunner:
    def __init__(
        self,
        registry: SkillRegistry | None = None,
        memory_store: MemoryStore | None = None,
    ) -> None:
        self.registry = registry or SkillRegistry()
        self.memory_store = memory_store or MemoryStore()

    def run_skill(self, skill_name: str, input_data: dict[str, Any] | None = None) -> RunResult:
        input_data = input_data or {}
        run_id = str(uuid4())
        started_at = datetime.now(timezone.utc).isoformat()
        start = time.perf_counter()

        try:
            skill_fn = self.registry.get_skill_callable(skill_name)
            output = skill_fn(input_data)
            duration_ms = int((time.perf_counter() - start) * 1000)
            result = RunResult(
                run_id=run_id,
                skill=skill_name,
                status="success",
                started_at=started_at,
                duration_ms=duration_ms,
                input=input_data,
                output=output,
            )
            self.memory_store.append_run(result.to_dict())
            return result
        except Exception as exc:
            duration_ms = int((time.perf_counter() - start) * 1000)
            result = RunResult(
                run_id=run_id,
                skill=skill_name,
                status="failed",
                started_at=started_at,
                duration_ms=duration_ms,
                input=input_data,
                error=str(exc),
                traceback=traceback.format_exc(),
            )
            self.memory_store.append_run(result.to_dict())
            return result


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
