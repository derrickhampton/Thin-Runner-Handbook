"""Command-line entrypoint for running a Thin Runner pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path

from .logging_utils import create_logger
from .memory import FileMemoryStore
from .registry import SkillRegistry
from .runner import run_pipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a Thin Runner pipeline")
    parser.add_argument(
        "--pipeline",
        default="pipelines/hello_pipeline.yaml",
        help="Path to a pipeline YAML file",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    logger = create_logger("thin_runner")
    memory = FileMemoryStore(
        memory_file=Path("memory/memory.md"),
        runs_file=Path("memory/runs.jsonl"),
    )
    registry = SkillRegistry.from_skills_directory(Path("skills"))
    result = run_pipeline(Path(args.pipeline), registry=registry, memory_store=memory, logger=logger)
    logger.info("Pipeline finished with %d step(s)", len(result.get("steps", [])))


if __name__ == "__main__":
    main()
