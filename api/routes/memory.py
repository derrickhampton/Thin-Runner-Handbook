from __future__ import annotations

from fastapi import APIRouter

from api.services.memory_service import MemoryService


router = APIRouter()
memory_service = MemoryService()


@router.get("/memory")
def get_memory() -> dict[str, str]:
    return memory_service.read_memory()
