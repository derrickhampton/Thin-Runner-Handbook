from __future__ import annotations

from typing import Any

from orchestrator.registry import SkillRegistry
from orchestrator.runner import ThinRunner


class SkillService:
    def __init__(self, config_path: str = "config/skills.example.yaml") -> None:
        self.registry = SkillRegistry.from_config(config_path)

    def list_skills(self) -> list[dict[str, Any]]:
        skills: list[dict[str, Any]] = []
        for name, cfg in self.registry.skills.items():
            cfg = cfg or {}
            skills.append(
                {
                    "name": name,
                    "path": cfg.get("path", ""),
                    "entrypoint": cfg.get("entrypoint", "run"),
                    "description": cfg.get("description", ""),
                }
            )
        return skills

    def run_skill(self, skill_name: str, input_data: dict[str, Any] | None = None) -> dict[str, Any]:
        runner = ThinRunner(registry=self.registry)
        return runner.run_skill(skill_name, input_data or {}).to_dict()
