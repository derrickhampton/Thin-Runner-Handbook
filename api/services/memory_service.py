from __future__ import annotations

from pathlib import Path


class MemoryService:
    def __init__(self, memory_path: str = "memory/memory.md") -> None:
        self.memory_path = Path(memory_path)

    def read_memory(self) -> dict[str, str]:
        content = ""
        if self.memory_path.exists():
            content = self.memory_path.read_text(encoding="utf-8")
        return {
            "path": str(self.memory_path),
            "content": content,
        }
