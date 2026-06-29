from __future__ import annotations

from typing import Any

from backend.core.event_bus import EventBus
from backend.core.health_monitor import HealthMonitor
from backend.memory.registry import discover_agents
from backend.memory.service import MemoryEngine


def build_system_status(
    *,
    version: str,
    memory_engine: MemoryEngine,
    event_bus: EventBus | None = None,
    health_monitor: HealthMonitor | None = None,
) -> dict[str, Any]:
    agents = discover_agents()
    memory_snapshot = memory_engine.list()[:5]
    event_metrics = event_bus.metrics() if event_bus else {"published_events": 0, "subscribers": {}, "topics": {}}
    health_summary = health_monitor.summary() if health_monitor else {"status": "unknown", "checks": {}}
    return {
        "status": "ok",
        "version": version,
        "components": {
            "memory": {"status": "ready", "entries": len(memory_snapshot)},
            "agent_registry": {"status": "ready", "count": len(agents)},
            "event_bus": {"status": "ready", **event_metrics},
            "health_monitor": health_summary,
            "api": {"status": "ready"},
        },
        "plugins": [
            {"name": agent["name"], "status": agent["status"]} for agent in agents
        ],
    }
