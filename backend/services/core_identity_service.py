from __future__ import annotations

from pathlib import Path
from typing import Any


DOCTRINE_FILES = {
    "constitution": Path("SALUS_CONSTITUTION.md"),
    "operating_doctrine": Path("SALUS_OPERATING_DOCTRINE.md"),
    "agent_standard": Path("SALUS_AGENT_STANDARD.md"),
    "decision_standard": Path("SALUS_DECISION_STANDARD.md"),
    "memory_standard": Path("SALUS_MEMORY_STANDARD.md"),
}


def read_doctrine_file(key: str) -> dict[str, Any]:
    if key not in DOCTRINE_FILES:
        raise KeyError(f"unknown doctrine key: {key}")

    path = DOCTRINE_FILES[key]

    return {
        "key": key,
        "path": str(path),
        "exists": path.exists(),
        "content": path.read_text() if path.exists() else "",
    }


def core_identity_status() -> dict[str, Any]:
    files = {key: read_doctrine_file(key) for key in DOCTRINE_FILES}

    return {
        "status": "ok",
        "module": "core_identity",
        "identity": "Project Salus is a Human Judgment System for the Intelligence Age.",
        "prime_directive": "Improve human judgment without replacing human accountability.",
        "doctrine_count": len(files),
        "doctrine_files": {
            key: {
                "path": value["path"],
                "exists": value["exists"],
                "content_length": len(value["content"]),
            }
            for key, value in files.items()
        },
        "core_loop": [
            "Observe",
            "Understand",
            "Evaluate",
            "Decide",
            "Execute",
            "Reflect",
            "Learn",
            "Improve",
        ],
    }


def core_identity_bundle() -> dict[str, Any]:
    return {
        "status": "ok",
        "module": "core_identity",
        "summary": core_identity_status(),
        "doctrine": {
            key: read_doctrine_file(key)
            for key in DOCTRINE_FILES
        },
    }
