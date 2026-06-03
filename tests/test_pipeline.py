from pathlib import Path

from orchestrator.pipeline import PipelineRunner


class _Result:
    def __init__(self, payload: dict):
        self._payload = payload

    def to_dict(self) -> dict:
        return self._payload


class _RunnerAlwaysSuccess:
    def __init__(self):
        self.calls: list[str] = []

    def run_skill(self, skill_name: str, input_data: dict):
        self.calls.append(skill_name)
        return _Result(
            {
                "run_id": f"run-{len(self.calls)}",
                "skill": skill_name,
                "status": "success",
                "started_at": "2026-01-01T00:00:00+00:00",
                "duration_ms": 1,
                "input": input_data,
                "output": {"ok": True},
                "error": None,
                "traceback": None,
            }
        )


class _RunnerFailsFirst:
    def __init__(self):
        self.calls: list[str] = []

    def run_skill(self, skill_name: str, input_data: dict):
        self.calls.append(skill_name)
        if len(self.calls) == 1:
            return _Result(
                {
                    "run_id": "run-1",
                    "skill": skill_name,
                    "status": "failed",
                    "started_at": "2026-01-01T00:00:00+00:00",
                    "duration_ms": 1,
                    "input": input_data,
                    "output": None,
                    "error": "boom",
                    "traceback": "trace",
                }
            )
        return _Result(
            {
                "run_id": "run-2",
                "skill": skill_name,
                "status": "success",
                "started_at": "2026-01-01T00:00:00+00:00",
                "duration_ms": 1,
                "input": input_data,
                "output": {"ok": True},
                "error": None,
                "traceback": None,
            }
        )


def test_pipeline_runner_runs_multiple_steps(tmp_path: Path) -> None:
    pipeline_file = tmp_path / "pipeline.yaml"
    pipeline_file.write_text(
        """
name: sample_pipeline
steps:
  - name: first
    skill: hello_world
    input: {name: A}
  - name: second
    skill: hello_world
    input: {name: B}
""".strip(),
        encoding="utf-8",
    )

    runner = _RunnerAlwaysSuccess()
    result = PipelineRunner(runner=runner).run_pipeline(pipeline_file)

    assert result["pipeline"] == "sample_pipeline"
    assert result["status"] == "success"
    assert len(result["steps"]) == 2
    assert result["steps"][0]["step_name"] == "first"
    assert result["steps"][1]["step_name"] == "second"
    assert runner.calls == ["hello_world", "hello_world"]


def test_pipeline_runner_stops_on_failed_step(tmp_path: Path) -> None:
    pipeline_file = tmp_path / "pipeline.yaml"
    pipeline_file.write_text(
        """
name: failing_pipeline
steps:
  - name: first
    skill: hello_world
    input: {name: A}
  - name: second
    skill: hello_world
    input: {name: B}
""".strip(),
        encoding="utf-8",
    )

    runner = _RunnerFailsFirst()
    result = PipelineRunner(runner=runner).run_pipeline(pipeline_file)

    assert result["pipeline"] == "failing_pipeline"
    assert result["status"] == "failed"
    assert len(result["steps"]) == 1
    assert result["steps"][0]["status"] == "failed"
    assert runner.calls == ["hello_world"]
