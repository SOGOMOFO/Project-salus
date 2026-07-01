from __future__ import annotations

from fastapi import APIRouter, Header, Request

from backend.core.agent_runtime import AgentRuntime
from backend.core.event_bus import EventBus
from backend.core.health_monitor import HealthMonitor
from backend.core.mission_planner import MissionPlanner
from backend.core.status import build_system_status
from backend.memory.service import MemoryEngine


def create_commander_router(
    *,
    agent_runtime: AgentRuntime,
    mission_planner: MissionPlanner,
    memory_engine: MemoryEngine,
    event_bus: EventBus,
    health_monitor: HealthMonitor,
    verify_passphrase,
    version: str,
) -> APIRouter:
    router = APIRouter(tags=["salus-core-v2"])

    def _authorize(
        x_salus_passphrase: str | None,
        *,
        action: str,
        role: str | None,
        x_salus_token: str | None,
        allowed_roles: set[str],
    ) -> None:
        try:
            verify_passphrase(
                x_salus_passphrase,
                action=action,
                role=role,
                x_salus_token=x_salus_token,
                allowed_roles=allowed_roles,
            )
        except TypeError:
            # Backward-compatible verifier support for unit tests that inject
            # the legacy one-argument passphrase checker.
            verify_passphrase(x_salus_passphrase)

    @router.get("/core")
    async def core_index():
        return {
            "status": "ok",
            "routes": [
                "/core/status",
                "/core/agents",
                "/core/agents/{name}/run",
                "/core/missions",
                "/core/missions/{mission_id}/complete",
                "/core/missions/{mission_id}",
                "/core/events",
                "/core/health",
            ],
        }

    @router.get("/core/status")
    async def core_status():
        payload = build_system_status(
            version=version,
            memory_engine=memory_engine,
            event_bus=event_bus,
            health_monitor=health_monitor,
        )
        payload["components"]["agent_runtime"] = {
            "status": "ready",
            "count": len(agent_runtime.list_agents()),
        }
        payload["components"]["mission_planner"] = {
            "status": "ready",
            "count": len(mission_planner.list_missions()),
        }
        return payload

    @router.get("/core/agents")
    async def core_agents(
        x_salus_passphrase: str | None = Header(default=None),
        x_salus_token: str | None = Header(default=None),
        x_salus_role: str | None = Header(default=None),
    ):
        _authorize(
            x_salus_passphrase,
            action="core.agents.read",
            role=x_salus_role,
            x_salus_token=x_salus_token,
            allowed_roles={"commander", "family", "agent", "readonly"},
        )
        return {"status": "ok", "agents": agent_runtime.list_agents()}

    @router.post("/core/agents/{name}/run")
    async def run_core_agent(
        name: str,
        request: Request,
        x_salus_passphrase: str | None = Header(default=None),
        x_salus_token: str | None = Header(default=None),
        x_salus_role: str | None = Header(default=None),
    ):
        _authorize(
            x_salus_passphrase,
            action="core.agents.run",
            role=x_salus_role,
            x_salus_token=x_salus_token,
            allowed_roles={"commander", "family", "agent"},
        )
        data = await request.json()
        if not isinstance(data, dict):
            data = {}
        result = agent_runtime.run_agent(
            name,
            data.get("input", {}),
            important=bool(data.get("important", False)),
        )
        event_bus.publish("agent.run", {"name": name, "status": result.get("status")})
        return result

    @router.get("/core/missions")
    async def core_missions(
        x_salus_passphrase: str | None = Header(default=None),
        x_salus_token: str | None = Header(default=None),
        x_salus_role: str | None = Header(default=None),
    ):
        _authorize(
            x_salus_passphrase,
            action="core.missions.read",
            role=x_salus_role,
            x_salus_token=x_salus_token,
            allowed_roles={"commander", "family", "agent", "readonly"},
        )
        return {"status": "ok", "missions": mission_planner.list_missions()}

    @router.post("/core/missions")
    async def create_core_mission(
        request: Request,
        x_salus_passphrase: str | None = Header(default=None),
        x_salus_token: str | None = Header(default=None),
        x_salus_role: str | None = Header(default=None),
    ):
        _authorize(
            x_salus_passphrase,
            action="core.missions.create",
            role=x_salus_role,
            x_salus_token=x_salus_token,
            allowed_roles={"commander", "family", "agent"},
        )
        data = await request.json()
        if not isinstance(data, dict):
            data = {}
        mission = mission_planner.create_mission(
            title=str(data.get("title", "")).strip(),
            description=str(data.get("description", "")).strip(),
            priority=str(data.get("priority", "medium")).strip(),
        )
        event_bus.publish("mission.created", {"id": mission["id"], "priority": mission["priority"]})
        return {"status": "created", "mission": mission}


    @router.patch("/core/missions/{mission_id}")
    async def update_core_mission(
        mission_id: int,
        request: Request,
        x_salus_passphrase: str | None = Header(default=None),
        x_salus_token: str | None = Header(default=None),
        x_salus_role: str | None = Header(default=None),
    ):
        _authorize(
            x_salus_passphrase,
            action="core.missions.update",
            role=x_salus_role,
            x_salus_token=x_salus_token,
            allowed_roles={"commander", "family", "agent"},
        )
        data = await request.json()
        if not isinstance(data, dict):
            data = {}

        mission = mission_planner.update_mission(
            mission_id,
            title=data.get("title"),
            description=data.get("description"),
            priority=data.get("priority"),
            status=data.get("status"),
        )

        if not mission:
            return {"status": "not_found", "id": mission_id}

        event_bus.publish(
            "mission.updated",
            {
                "id": mission_id,
                "priority": mission["priority"],
                "status": mission["status"],
            },
        )
        return {"status": "updated", "mission": mission}

    @router.post("/core/missions/{mission_id}/complete")
    async def complete_core_mission(
        mission_id: int,
        x_salus_passphrase: str | None = Header(default=None),
        x_salus_token: str | None = Header(default=None),
        x_salus_role: str | None = Header(default=None),
    ):
        _authorize(
            x_salus_passphrase,
            action="core.missions.complete",
            role=x_salus_role,
            x_salus_token=x_salus_token,
            allowed_roles={"commander", "family", "agent"},
        )
        mission = mission_planner.complete_mission(mission_id)
        if not mission:
            return {"status": "not_found", "id": mission_id}
        event_bus.publish("mission.completed", {"id": mission_id})
        return {"status": "completed", "mission": mission}

    @router.get("/core/events")
    async def core_events(
        x_salus_passphrase: str | None = Header(default=None),
        topic: str | None = None,
        limit: int = 20,
        x_salus_token: str | None = Header(default=None),
        x_salus_role: str | None = Header(default=None),
    ):
        _authorize(
            x_salus_passphrase,
            action="core.events.read",
            role=x_salus_role,
            x_salus_token=x_salus_token,
            allowed_roles={"commander", "family", "agent", "readonly"},
        )
        return {
            "status": "ok",
            "events": event_bus.history(topic=topic, limit=limit),
            "metrics": event_bus.metrics(),
        }

    @router.get("/core/health")
    async def core_health(
        x_salus_passphrase: str | None = Header(default=None),
        x_salus_token: str | None = Header(default=None),
        x_salus_role: str | None = Header(default=None),
    ):
        _authorize(
            x_salus_passphrase,
            action="core.health.read",
            role=x_salus_role,
            x_salus_token=x_salus_token,
            allowed_roles={"commander", "family", "agent", "readonly"},
        )
        health_monitor.record_check("api", "ok", "Core API responsive")
        health_monitor.record_check("agent_runtime", "ready", "Agents loaded")
        health_monitor.record_check("mission_planner", "ready", "Planner available")
        return health_monitor.summary()

    return router
