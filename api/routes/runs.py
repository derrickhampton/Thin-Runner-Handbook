from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from api.services.run_service import RunService


router = APIRouter()
run_service = RunService()


@router.get("/runs")
def list_runs(limit: int = Query(default=25, ge=1, le=250)) -> dict[str, list[dict[str, Any]]]:
    return {"runs": run_service.list_runs(limit=limit)}


@router.get("/runs/{run_id}/log")
def get_run_log(run_id: str) -> dict[str, Any]:
    try:
        return run_service.get_run_log(run_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
