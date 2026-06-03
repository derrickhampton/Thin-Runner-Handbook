from pathlib import Path

from orchestrator.memory import FileMemoryStore
from orchestrator.registry import SkillRegistry
from orchestrator.runner import ThinRunner, run_pipeline


class _Logger:
    def info(self, *_args, **_kwargs):
        return None


class _SuccessRegistry:
    def get_skill_callable(self, skill_name: str):
        assert skill_name == "hello_world"

        def _fn(payload: dict):
            return {
                "message": f"Hello, {payload.get('name', 'Thin Runner')}!",
                "skill": "hello_world",
                "status": "success",
            }

        return _fn


class _FailureRegistry:
    def get_skill_callable(self, _skill_name: str):
        def _fn(_payload: dict):
            raise RuntimeError("skill blew up")

        return _fn


def test_run_hello_pipeline(tmp_path: Path) -> None:
    memory = FileMemoryStore(
        memory_file=tmp_path / "memory.md",
        runs_file=tmp_path / "runs.jsonl",
    )
    registry = SkillRegistry.from_config(Path("config/skills.example.yaml"))
    result = run_pipeline(
        Path("pipelines/hello_pipeline.yaml"),
        registry=registry,
        memory_store=memory,
        logger=_Logger(),
    )

    assert result["pipeline"] == "hello-pipeline"
    assert len(result["steps"]) == 1
    assert result["steps"][0]["output"]["message"] == "Hello, Handbook!"


def test_thin_runner_run_skill_success() -> None:
    runner = ThinRunner(registry=_SuccessRegistry())
    result = runner.run_skill("hello_world", {"name": "Thin Runner"})

    assert result.status == "success"
    assert result.output is not None
    assert result.output["message"] == "Hello, Thin Runner!"
    assert result.run_id
    assert result.started_at
    assert result.duration_ms >= 0


def test_thin_runner_run_skill_failure_has_error_details() -> None:
    runner = ThinRunner(registry=_FailureRegistry())
    result = runner.run_skill("hello_world", {"name": "Thin Runner"})

    assert result.status == "failed"
    assert result.output is None
    assert "skill blew up" in (result.error or "")
    assert "RuntimeError" in (result.traceback or "")
    assert result.run_id
    assert result.started_at
    assert result.duration_ms >= 0
