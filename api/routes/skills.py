from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.services.skill_service import SkillService


router = APIRouter()
skill_service = SkillService()


class SkillRunRequest(BaseModel):
    input: dict[str, Any] = {}


@router.get("/skills")
def list_skills() -> dict[str, list[dict[str, Any]]]:
    return {"skills": skill_service.list_skills()}


@router.post("/skills/{skill_name}/run")
def run_skill(skill_name: str, request: SkillRunRequest) -> dict[str, Any]:
    try:
        return skill_service.run_skill(skill_name, request.input)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
