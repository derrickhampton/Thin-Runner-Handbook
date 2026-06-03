"""Hello world skill."""

from __future__ import annotations


def run(payload: dict) -> dict:
    name = payload.get("name", "Thin Runner")
    return {
        "message": f"Hello, {name}!",
        "skill": "hello_world",
        "status": "success",
    }
