"""Command-line interface for Thin Runner."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .pipeline import PipelineRunner
from .runner import ThinRunner


def _load_input(args: argparse.Namespace) -> dict[str, Any]:
    if args.json_input:
        return json.loads(args.json_input)

    if args.input:
        return json.loads(Path(args.input).read_text(encoding="utf-8"))

    return {}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Thin Runner Handbook CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_skill = subparsers.add_parser("run-skill", help="Run a skill by name")
    run_skill.add_argument("skill_name")
    run_skill.add_argument("--input", help="Path to JSON input file")
    run_skill.add_argument("--json", dest="json_input", help="Inline JSON input")

    run_pipeline = subparsers.add_parser("run-pipeline", help="Run a pipeline by YAML path")
    run_pipeline.add_argument("pipeline_path")

    args = parser.parse_args(argv)

    if args.command == "run-skill":
        try:
            input_data = _load_input(args)
            result = ThinRunner().run_skill(args.skill_name, input_data)
            print(json.dumps(result.to_dict(), indent=2))
            return 0 if result.status == "success" else 1
        except Exception as exc:
            print(json.dumps({"status": "failed", "error": str(exc)}, indent=2), file=sys.stderr)
            return 1

    if args.command == "run-pipeline":
        try:
            result = PipelineRunner().run_pipeline(args.pipeline_path)
            print(json.dumps(result, indent=2))
            return 0 if result.get("status") == "success" else 1
        except Exception as exc:
            print(json.dumps({"status": "failed", "error": str(exc)}, indent=2), file=sys.stderr)
            return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
