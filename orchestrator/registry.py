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
    """Load a skill module, registering it as a proper package submodule when
    the skill directory contains an ``__init__.py``.

    This ensures the module lives under a stable dotted name in ``sys.modules``
    (e.g. ``skills.hello_world.run``) so that ``unittest.mock.patch`` targets
    the same object that absolute imports resolve.
    """
    import sys

    parent_dir = path.parent
    init_file = parent_dir / "__init__.py"

    if init_file.exists():
        # Derive a dotted package name from the directory structure.
        # e.g.  skills/hello_world/run.py  ->  "skills.hello_world.run"
        package_name = f"{parent_dir.parent.name}.{parent_dir.name}"
        full_name = f"{package_name}.{path.stem}"

        # Return a cached module if it has already been loaded.
        if full_name in sys.modules:
            return sys.modules[full_name]

        # Ensure the parent package is registered so relative/absolute imports
        # inside run.py can resolve sibling modules.
        if package_name not in sys.modules:
            pkg_spec = importlib.util.spec_from_file_location(
                package_name,
                init_file,
                submodule_search_locations=[str(parent_dir)],
            )
            if pkg_spec and pkg_spec.loader:
                pkg_module = importlib.util.module_from_spec(pkg_spec)
                pkg_module.__package__ = package_name
                pkg_module.__path__ = [str(parent_dir)]  # type: ignore[assignment]
                sys.modules[package_name] = pkg_module
                pkg_spec.loader.exec_module(pkg_module)

        use_name = full_name
    else:
        use_name = module_name

    spec = importlib.util.spec_from_file_location(use_name, path)
    if spec is None or spec.loader is None:
        raise SkillRegistryError(f"Could not load skill module from: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[use_name] = module
    spec.loader.exec_module(module)
    return module
