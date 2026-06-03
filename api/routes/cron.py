from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from api.services.cron_service import CronService


router = APIRouter()
cron_service = CronService()


class CronUpdateRequest(BaseModel):
    enabled: bool = True
    schedule: str
    command: str


@router.get("/cron")
def get_cron() -> dict[str, Any]:
    try:
        return cron_service.get_managed_schedule()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.put("/cron")
def update_cron(request: CronUpdateRequest) -> dict[str, Any]:
    try:
        return cron_service.update_schedule(
            enabled=request.enabled,
            schedule=request.schedule,
            command=request.command,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
