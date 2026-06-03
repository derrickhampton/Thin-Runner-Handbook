from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.routes.cron import router as cron_router
from api.routes.memory import router as memory_router
from api.routes.runs import router as runs_router
from api.routes.skills import router as skills_router


app = FastAPI(title="Thin Runner Dashboard API")

app.include_router(skills_router, prefix="/api")
app.include_router(runs_router, prefix="/api")
app.include_router(memory_router, prefix="/api")
app.include_router(cron_router, prefix="/api")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "thin-runner-dashboard"}


ui_dir = Path("ui")
if ui_dir.exists():
    app.mount("/ui", StaticFiles(directory=str(ui_dir), html=True), name="ui")


@app.get("/")
def dashboard_index() -> FileResponse:
    return FileResponse("ui/index.html")
