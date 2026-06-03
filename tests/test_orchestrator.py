from pathlib import Path

from orchestrator.memory import FileMemoryStore
from orchestrator.registry import SkillRegistry
from orchestrator.runner import run_pipeline


class _Logger:
    def info(self, *_args, **_kwargs):
        return None


def test_run_hello_pipeline(tmp_path: Path) -> None:
    memory = FileMemoryStore(
        memory_file=tmp_path / "memory.md",
        runs_file=tmp_path / "runs.jsonl",
    )
    registry = SkillRegistry.from_skills_directory(Path("skills"))
    result = run_pipeline(
        Path("pipelines/hello_pipeline.yaml"),
        registry=registry,
        memory_store=memory,
        logger=_Logger(),
    )

    assert result["pipeline"] == "hello-pipeline"
    assert len(result["steps"]) == 1
    assert result["steps"][0]["output"]["message"] == "Hello, Handbook!"
