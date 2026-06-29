from __future__ import annotations

from typing import Any

from backend.memory.registry import discover_agents
from backend.memory.service import MemoryEngine


def build_system_status(*, version: str, memory_engine: MemoryEngine) -> dict[str, Any]:
    agents = discover_agents()
    memory_snapshot = memory_engine.list()[:5]
    return {
        "status": "ok",
        "version": version,
        "components": {
            "memory": {"status": "ready", "entries": len(memory_snapshot)},
            "agent_registry": {"status": "ready", "count": len(agents)},
            "api": {"status": "ready"},
        },
        "plugins": [
            {"name": agent["name"], "status": agent["status"]} for agent in agents
        ],
    }
