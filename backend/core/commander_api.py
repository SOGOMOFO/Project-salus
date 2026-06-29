from __future__ import annotations

from fastapi import APIRouter, Header, Request

from backend.core.agent_runtime import AgentRuntime
from backend.core.mission_planner import MissionPlanner
from backend.core.status import build_system_status
from backend.memory.service import MemoryEngine


def create_commander_router(
    *,
    agent_runtime: AgentRuntime,
    mission_planner: MissionPlanner,
    memory_engine: MemoryEngine,
    verify_passphrase,
    version: str,
) -> APIRouter:
    router = APIRouter(tags=["salus-core-v2"])

    @router.get("/core/status")
    async def core_status():
        payload = build_system_status(version=version, memory_engine=memory_engine)
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
    async def core_agents(x_salus_passphrase: str | None = Header(default=None)):
        verify_passphrase(x_salus_passphrase)
        return {"status": "ok", "agents": agent_runtime.list_agents()}

    @router.post("/core/agents/{name}/run")
    async def run_core_agent(
        name: str,
        request: Request,
        x_salus_passphrase: str | None = Header(default=None),
    ):
        verify_passphrase(x_salus_passphrase)
        data = await request.json()
        if not isinstance(data, dict):
            data = {}
        return agent_runtime.run_agent(
            name,
            data.get("input", {}),
            important=bool(data.get("important", False)),
        )

    @router.get("/core/missions")
    async def core_missions(x_salus_passphrase: str | None = Header(default=None)):
        verify_passphrase(x_salus_passphrase)
        return {"status": "ok", "missions": mission_planner.list_missions()}

    @router.post("/core/missions")
    async def create_core_mission(
        request: Request,
        x_salus_passphrase: str | None = Header(default=None),
    ):
        verify_passphrase(x_salus_passphrase)
        data = await request.json()
        if not isinstance(data, dict):
            data = {}
        mission = mission_planner.create_mission(
            title=str(data.get("title", "")).strip(),
            description=str(data.get("description", "")).strip(),
            priority=str(data.get("priority", "medium")).strip(),
        )
        return {"status": "created", "mission": mission}

    @router.post("/core/missions/{mission_id}/complete")
    async def complete_core_mission(
        mission_id: int,
        x_salus_passphrase: str | None = Header(default=None),
    ):
        verify_passphrase(x_salus_passphrase)
        mission = mission_planner.complete_mission(mission_id)
        if not mission:
            return {"status": "not_found", "id": mission_id}
        return {"status": "completed", "mission": mission}

    return router
