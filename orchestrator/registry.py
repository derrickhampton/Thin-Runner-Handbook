"""Skill registry and loader based on explicit YAML configuration."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable
from types import ModuleType

import yaml


class SkillRegistryError(Exception):
    """Raised for skill registry and loading failures."""


class SkillRegistry:
    def __init__(self, config_path: str | Path = "config/skills.example.yaml"):
        self.config_path = Path(config_path)
        self.skills = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        if not self.config_path.exists():
            raise SkillRegistryError(f"Skill config not found: {self.config_path}")

        data = yaml.safe_load(self.config_path.read_text(encoding="utf-8")) or {}
        skills = data.get("skills", {})
        if not isinstance(skills, dict):
            raise SkillRegistryError("Skill config 'skills' must be a mapping")
        return skills

    @classmethod
    def from_config(cls, config_path: str | Path = "config/skills.example.yaml") -> "SkillRegistry":
        return cls(config_path=config_path)

    def get_skill_callable(self, skill_name: str) -> Callable[[dict[str, Any]], dict[str, Any]]:
        if skill_name not in self.skills:
            raise SkillRegistryError(f"Unknown skill: {skill_name}")

        skill_config = self.skills[skill_name]
        if not isinstance(skill_config, dict):
            raise SkillRegistryError(f"Invalid config for skill: {skill_name}")

        path_str = skill_config.get("path")
        if not path_str:
            raise SkillRegistryError(f"Skill {skill_name} missing required 'path'")

        path = Path(path_str)
        entrypoint = skill_config.get("entrypoint", "run")

        if not path.exists():
            raise SkillRegistryError(f"Skill file not found: {path}")

        module = _load_module_from_path(f"thin_runner_skill_{skill_name}", path)

        fn = getattr(module, entrypoint, None)
        if not callable(fn):
            raise SkillRegistryError(
                f"Skill {skill_name} missing callable entrypoint: {entrypoint}"
            )

        return fn

    def get(self, name: str) -> Callable:
        return self.get_skill_callable(name)


def _load_module_from_path(module_name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise SkillRegistryError(f"Could not load skill module from: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
