"""Skill discovery and lookup."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType
from typing import Callable


class SkillRegistry:
    def __init__(self, skills: dict[str, Callable]):
        self._skills = skills

    @classmethod
    def from_skills_directory(cls, skills_dir: Path) -> "SkillRegistry":
        discovered: dict[str, Callable] = {}
        for run_file in skills_dir.glob("*/run.py"):
            skill_name = run_file.parent.name
            module = _load_module_from_path(f"skill_{skill_name}", run_file)
            discovered[skill_name] = getattr(module, "run")
        return cls(discovered)

    def get(self, name: str) -> Callable:
        if name not in self._skills:
            known = ", ".join(sorted(self._skills))
            raise KeyError(f"Unknown skill '{name}'. Known skills: {known}")
        return self._skills[name]


def _load_module_from_path(module_name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
