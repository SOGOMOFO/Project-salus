from __future__ import annotations

from typing import Any


SUBSYSTEMS = {
    "core_identity": {
        "name": "Core Identity",
        "layer": "command",
        "status_route": "/api/core-identity/status",
        "command_route": "/command/core-identity",
        "mission": "Expose Salus doctrine, standards, and prime directive.",
    },
    "knowledge": {
        "name": "Knowledge Engine",
        "layer": "memory",
        "status_route": "/api/knowledge/status",
        "command_route": "/command/knowledge",
        "mission": "Capture structured knowledge that improves judgment.",
    },
    "memory": {
        "name": "Memory Engine",
        "layer": "memory",
        "status_route": "/api/memory/status",
        "command_route": "/command/memory",
        "mission": "Maintain continuity across user, mission, and knowledge memory.",
    },
    "judgment": {
        "name": "Judgment Engine",
        "layer": "reasoning",
        "status_route": "/api/judgment-engine/status",
        "command_route": "/command/judgment",
        "mission": "Score and structure decisions using evidence, risks, confidence, and next action.",
    },
    "kernel": {
        "name": "Salus Kernel",
        "layer": "command",
        "status_route": "/api/kernel/status",
        "command_route": "/command/kernel",
        "mission": "Central orchestration layer for Salus OS.",
    },
}


def list_subsystems() -> list[dict[str, Any]]:
    return [
        {"id": subsystem_id, **definition}
        for subsystem_id, definition in sorted(SUBSYSTEMS.items())
    ]


def get_subsystem(subsystem_id: str) -> dict[str, Any] | None:
    definition = SUBSYSTEMS.get(subsystem_id)
    if definition is None:
        return None
    return {"id": subsystem_id, **definition}


def subsystem_registry_status() -> dict[str, Any]:
    subsystems = list_subsystems()
    layers = sorted({subsystem["layer"] for subsystem in subsystems})

    return {
        "status": "ok",
        "module": "subsystem_registry",
        "subsystem_count": len(subsystems),
        "layers": layers,
        "subsystems": subsystems,
    }


def route_for_intent(intent: str) -> dict[str, Any]:
    mapping = {
        "learning": "knowledge",
        "judgment": "judgment",
        "memory": "memory",
        "command": "kernel",
        "agent": "kernel",
        "general": "core_identity",
    }

    subsystem_id = mapping.get(intent, "core_identity")
    subsystem = get_subsystem(subsystem_id)

    return {
        "intent": intent,
        "subsystem_id": subsystem_id,
        "subsystem": subsystem,
    }
