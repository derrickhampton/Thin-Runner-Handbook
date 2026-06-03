"""Hello world skill."""

from __future__ import annotations

from typing import Any


def run(input_data: dict[str, Any] | None = None) -> dict[str, Any]:
    """Return a predictable hello-world response."""
    input_data = input_data or {}
    name = str(input_data.get("name") or "Thin Runner").strip() or "Thin Runner"

    return {
        "message": f"Hello, {name}!",
        "skill": "hello_world",
        "status": "success",
    }
