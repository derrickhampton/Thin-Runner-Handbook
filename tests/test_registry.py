from pathlib import Path

import pytest

from orchestrator.registry import SkillRegistry, SkillRegistryError


def _write_config(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    return path


def test_registry_loads_config_and_resolves_hello_world() -> None:
    registry = SkillRegistry.from_config("config/skills.example.yaml")
    fn = registry.get_skill_callable("hello_world")
    result = fn({"name": "Thin Runner"})
    assert result["message"] == "Hello, Thin Runner!"


def test_registry_raises_clear_error_for_unknown_skill() -> None:
    registry = SkillRegistry.from_config("config/skills.example.yaml")
    with pytest.raises(SkillRegistryError, match="Unknown skill: does_not_exist"):
        registry.get_skill_callable("does_not_exist")


def test_registry_raises_clear_error_for_missing_file(tmp_path: Path) -> None:
    config = _write_config(
        tmp_path / "skills.yaml",
        """
skills:
  bad_skill:
    path: skills/does_not_exist/run.py
    entrypoint: run
""".strip(),
    )
    registry = SkillRegistry.from_config(config)

    with pytest.raises(SkillRegistryError, match="Skill file not found"):
        registry.get_skill_callable("bad_skill")


def test_registry_raises_clear_error_for_missing_callable(tmp_path: Path) -> None:
    skill_file = tmp_path / "skill.py"
    skill_file.write_text("x = 1\n", encoding="utf-8")
    config = _write_config(
        tmp_path / "skills.yaml",
        f"""
skills:
  bad_entrypoint:
    path: {skill_file}
    entrypoint: run
""".strip(),
    )
    registry = SkillRegistry.from_config(config)

    with pytest.raises(SkillRegistryError, match="missing callable entrypoint"):
        registry.get_skill_callable("bad_entrypoint")
