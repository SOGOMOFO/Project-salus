from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

from backend.database import init_db, seed_data, get_connection
from backend.core.agent_runtime import AgentRuntime
from backend.core.event_bus import EventBus
from backend.core.health_monitor import HealthMonitor
from backend.core.mission_planner import MissionPlanner
from backend.core.commander_api import create_commander_router
from backend.core.intelligence_api import router as intelligence_router
from backend.core.status import build_system_status
from backend.directorates.investor_intelligence.api import router as investor_intelligence_router
from backend.api.memory import router as memory_router
from backend.forge.api import router as forge_router
from backend.memory.service import MemoryEngine
from backend.memory.memory_engine import initialize_memory_store
from backend.plugins.api import router as plugins_router
from backend.plugins.service import PluginService
from backend.security.api import router as security_router
from backend.security.core import security_core

SALUS_PASSPHRASE = os.getenv("SALUS_PASSPHRASE", "salus-secure")
memory_engine = MemoryEngine()
memory_engine.initialize()
initialize_memory_store()
agent_runtime = AgentRuntime()
agent_runtime.bootstrap_default_agents()
mission_planner = MissionPlanner()
mission_planner.initialize()
event_bus = EventBus()
health_monitor = HealthMonitor(name="project-salus")
plugin_service = PluginService()


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    seed_data()
    yield


app = FastAPI(
    title="Project Salus",
    version="0.4.0",
    description="Mission Control Backend with Security Layer",
    lifespan=lifespan,
)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = BASE_DIR / "frontend" / "templates" / "index.html"
STATIC_DIR = BASE_DIR / "frontend" / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.include_router(memory_router)
app.include_router(investor_intelligence_router)
app.include_router(plugins_router)
app.include_router(forge_router)
app.include_router(security_router)
app.include_router(intelligence_router)


def verify_passphrase(
    x_salus_passphrase: str | None,
    *,
    action: str = "legacy.protected",
    role: str | None = None,
    x_salus_token: str | None = None,
    allowed_roles: set[str] | None = None,
):
    security_core.authorize(
        action=action,
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=role,
        allowed_roles=allowed_roles,
    )


core_router = create_commander_router(
    agent_runtime=agent_runtime,
    mission_planner=mission_planner,
    memory_engine=memory_engine,
    event_bus=event_bus,
    health_monitor=health_monitor,
    verify_passphrase=verify_passphrase,
    version="0.4.0",
)
app.include_router(core_router)


@app.get("/", response_class=HTMLResponse)
async def home():
    return TEMPLATE_PATH.read_text()


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "0.4.0"}


async def plugin_health():
    return plugin_service.health()


@app.get("/system/status")
async def system_status():
    health_monitor.record_check("memory", "ready", "Persistent memory engine initialized")
    health_monitor.record_check("plugins", "ready", "Plugin service available")
    return build_system_status(
        version="0.4.0",
        memory_engine=memory_engine,
        event_bus=event_bus,
        health_monitor=health_monitor,
    )

@app.get("/status")
async def mission_control_status():
    return await system_status()


@app.get("/core/memory/status")
async def core_memory_status():
    memory_snapshot = memory_engine.list()[:5]
    return {
        "status": "ok",
        "memory": {
            "status": "ready",
            "entries": len(memory_snapshot),
            "sample": memory_snapshot,
        },
    }


# Re-export core handlers for direct unit tests that import from backend.main.
core_status = next(route.endpoint for route in core_router.routes if route.path == "/core/status" and "GET" in route.methods)
core_agents = next(route.endpoint for route in core_router.routes if route.path == "/core/agents" and "GET" in route.methods)
run_core_agent = next(route.endpoint for route in core_router.routes if route.path == "/core/agents/{name}/run" and "POST" in route.methods)
core_missions = next(route.endpoint for route in core_router.routes if route.path == "/core/missions" and "GET" in route.methods)
create_core_mission = next(route.endpoint for route in core_router.routes if route.path == "/core/missions" and "POST" in route.methods)
complete_core_mission = next(route.endpoint for route in core_router.routes if route.path == "/core/missions/{mission_id}/complete" and "POST" in route.methods)
investor_intelligence_status = next(
    route.endpoint for route in investor_intelligence_router.routes if route.path == "/investor-intelligence/status" and "GET" in route.methods
)
investor_intelligence_framework = next(
    route.endpoint for route in investor_intelligence_router.routes if route.path == "/investor-intelligence/framework" and "GET" in route.methods
)
investor_intelligence_analyze = next(
    route.endpoint for route in investor_intelligence_router.routes if route.path == "/investor-intelligence/analyze" and "POST" in route.methods
)
intelligence_status = next(
    route.endpoint for route in intelligence_router.routes if route.path == "/intelligence/status" and "GET" in route.methods
)
intelligence_evaluate = next(
    route.endpoint for route in intelligence_router.routes if route.path == "/intelligence/evaluate" and "POST" in route.methods
)
intelligence_reconcile = next(
    route.endpoint for route in intelligence_router.routes if route.path == "/intelligence/reconcile" and "POST" in route.methods
)

# Export endpoint callables for direct unit tests.
__all__ = [
    "app",
    "core_status",
    "core_agents",
    "run_core_agent",
    "core_missions",
    "create_core_mission",
    "complete_core_mission",
    "investor_intelligence_status",
    "investor_intelligence_framework",
    "investor_intelligence_analyze",
    "intelligence_status",
    "intelligence_evaluate",
    "intelligence_reconcile",
]


@app.get("/core/plugins/status")
async def core_plugins_status(
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    verify_passphrase(
        x_salus_passphrase,
        action="core.plugins.status.read",
        role=x_salus_role,
        x_salus_token=x_salus_token,
        allowed_roles={"commander", "family", "agent", "readonly"},
    )
    return await plugin_health()


@app.post("/auth")
async def auth(request: Request):
    data = await request.json()
    passphrase = data.get("passphrase", "")

    if passphrase == SALUS_PASSPHRASE:
        security_core.authorize(
            action="auth.passphrase.login",
            x_salus_passphrase=passphrase,
            x_salus_token=None,
            x_salus_role=str(data.get("role", "commander")),
            allowed_roles={"commander", "family", "agent", "readonly"},
        )
        return {
            "status": "authorized",
            "message": "Access granted to Project Salus Mission Control",
            "security_core": "v1",
            "passphrase_compatibility": True,
        }

    raise HTTPException(status_code=401, detail="Invalid passphrase")


@app.get("/missions")
async def missions(
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    verify_passphrase(
        x_salus_passphrase,
        action="missions.read",
        role=x_salus_role,
        x_salus_token=x_salus_token,
        allowed_roles={"commander", "family", "agent", "readonly"},
    )

    conn = get_connection()
    rows = conn.execute("SELECT * FROM missions ORDER BY id").fetchall()
    conn.close()
    return {"missions": [dict(row) for row in rows]}


@app.get("/agents")
async def agents(
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    verify_passphrase(
        x_salus_passphrase,
        action="agents.read",
        role=x_salus_role,
        x_salus_token=x_salus_token,
        allowed_roles={"commander", "family", "agent", "readonly"},
    )

    conn = get_connection()
    rows = conn.execute("SELECT * FROM agents ORDER BY id").fetchall()
    conn.close()
    return {"agents": [dict(row) for row in rows]}


@app.get("/sitreps")
async def sitreps(
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    verify_passphrase(
        x_salus_passphrase,
        action="sitreps.read",
        role=x_salus_role,
        x_salus_token=x_salus_token,
        allowed_roles={"commander", "family", "agent", "readonly"},
    )

    conn = get_connection()
    rows = conn.execute("SELECT * FROM sitreps ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    return {"sitreps": [dict(row) for row in rows]}


@app.post("/sitreps")
async def create_sitrep(
    request: Request,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    verify_passphrase(
        x_salus_passphrase,
        action="sitreps.create",
        role=x_salus_role,
        x_salus_token=x_salus_token,
        allowed_roles={"commander", "family", "agent"},
    )

    data = await request.json()
    conn = get_connection()
    conn.execute(
        "INSERT INTO sitreps (top_priority, blocker, action_1, action_2, action_3) VALUES (?,?,?,?,?)",
        (
            data.get("top_priority", ""),
            data.get("blocker", ""),
            data.get("action_1", ""),
            data.get("action_2", ""),
            data.get("action_3", ""),
        )
    )
    conn.commit()
    conn.close()
    return {"status": "created"}
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
@app.post("/api/judgment")
def create_judgment(payload: dict):
    from backend.core.intelligence_core import generate_judgment
    from backend.core.explainability_engine import explain_recommendation

    judgment = generate_judgment(**payload)
    explanation = explain_recommendation(judgment)

    return {
        "status": "ok",
        "judgment": judgment,
        "explanation": explanation,
    }


@app.post("/api/sitrep")
def api_create_sitrep(payload: dict):
    from backend.sitrep_service import create_sitrep

    try:
        sitrep = create_sitrep(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "ok",
        "sitrep": sitrep,
    }


@app.get("/api/sitrep")
def api_list_sitreps(limit: int = 10):
    from backend.sitrep_service import list_sitreps

    return {
        "status": "ok",
        "count": len(list_sitreps(limit=limit)),
        "sitreps": list_sitreps(limit=limit),
    }


@app.get("/api/sitrep/{sitrep_id}")
def api_get_sitrep(sitrep_id: int):
    from backend.sitrep_service import get_sitrep

    sitrep = get_sitrep(sitrep_id)

    if sitrep is None:
        raise HTTPException(status_code=404, detail="SITREP not found")

    return {
        "status": "ok",
        "sitrep": sitrep,
    }


@app.post("/api/aar")
def api_create_aar(payload: dict):
    from backend.aar_service import create_aar

    try:
        aar = create_aar(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "ok",
        "aar": aar,
    }


@app.get("/api/aar")
def api_list_aars(limit: int = 10):
    from backend.aar_service import list_aars

    aars = list_aars(limit=limit)

    return {
        "status": "ok",
        "count": len(aars),
        "aars": aars,
    }


@app.get("/api/aar/{aar_id}")
def api_get_aar(aar_id: int):
    from backend.aar_service import get_aar

    aar = get_aar(aar_id)

    if aar is None:
        raise HTTPException(status_code=404, detail="AAR not found")

    return {
        "status": "ok",
        "aar": aar,
    }


@app.get("/api/mvp/status")
def api_mvp_status():
    from backend.sitrep_service import list_sitreps
    from backend.aar_service import list_aars

    latest_sitreps = list_sitreps(limit=1)
    latest_aars = list_aars(limit=1)
    missions = mission_planner.list_missions()

    open_missions = [
        mission for mission in missions
        if mission.get("status") != "completed"
    ]

    return {
        "status": "ok",
        "mvp": {
            "heartbeat": "alive",
            "loop": {
                "plan": bool(latest_sitreps),
                "execute": bool(missions),
                "learn": bool(latest_aars),
            },
            "capabilities": {
                "judgment_api": True,
                "daily_sitrep": True,
                "mission_tracker": True,
                "aar_log": True,
                "sqlite_persistence": True,
            },
            "counts": {
                "sitreps": len(latest_sitreps),
                "open_missions": len(open_missions),
                "aars": len(latest_aars),
            },
            "latest_sitrep": latest_sitreps[0] if latest_sitreps else None,
            "latest_aar": latest_aars[0] if latest_aars else None,
            "open_missions": open_missions,
        },
    }


@app.get("/api/commander/today")
def api_commander_today():
    from backend.sitrep_service import list_sitreps
    from backend.aar_service import list_aars

    latest_sitreps = list_sitreps(limit=1)
    latest_aars = list_aars(limit=1)
    missions = mission_planner.list_missions()

    open_missions = [
        mission for mission in missions
        if mission.get("status") != "completed"
    ]

    blocked_missions = [
        mission for mission in open_missions
        if mission.get("status") == "blocked"
    ]

    high_priority_open = [
        mission for mission in open_missions
        if mission.get("priority") == "high"
    ]

    if blocked_missions:
        next_recommended_action = "Resolve blocked mission before starting new work."
    elif high_priority_open:
        next_recommended_action = f"Execute high-priority mission: {high_priority_open[0]['title']}"
    elif latest_sitreps:
        next_recommended_action = latest_sitreps[0].get("action_1") or "Execute today's SITREP priority."
    else:
        next_recommended_action = "Create today's SITREP."

    return {
        "status": "ok",
        "commander_today": {
            "operating_status": "active",
            "latest_sitrep": latest_sitreps[0] if latest_sitreps else None,
            "latest_aar": latest_aars[0] if latest_aars else None,
            "open_missions": open_missions,
            "blocked_missions": blocked_missions,
            "next_recommended_action": next_recommended_action,
        },
    }


def _build_commander_snapshot():
    from backend.sitrep_service import list_sitreps
    from backend.aar_service import list_aars

    latest_sitreps = list_sitreps(limit=1)
    latest_aars = list_aars(limit=1)
    missions = mission_planner.list_missions()

    open_missions = [
        mission for mission in missions
        if mission.get("status") != "completed"
    ]

    blocked_missions = [
        mission for mission in open_missions
        if mission.get("status") == "blocked"
    ]

    high_priority_open = [
        mission for mission in open_missions
        if mission.get("priority") == "high"
    ]

    latest_sitrep = latest_sitreps[0] if latest_sitreps else None
    latest_aar = latest_aars[0] if latest_aars else None

    if blocked_missions:
        next_action = "Resolve blocked mission before starting new work."
    elif high_priority_open:
        next_action = f"Execute high-priority mission: {high_priority_open[0]['title']}"
    elif latest_sitrep:
        next_action = latest_sitrep.get("action_1") or "Execute today's SITREP priority."
    else:
        next_action = "Create today's SITREP."

    return {
        "operating_status": "active",
        "latest_sitrep": latest_sitrep,
        "latest_aar": latest_aar,
        "missions": missions,
        "open_missions": open_missions,
        "blocked_missions": blocked_missions,
        "high_priority_open": high_priority_open,
        "next_recommended_action": next_action,
    }


@app.get("/api/commander/brief")
def api_commander_brief():
    snapshot = _build_commander_snapshot()

    latest_sitrep = snapshot["latest_sitrep"]
    latest_aar = snapshot["latest_aar"]

    brief_lines = [
        "PROJECT SALUS COMMANDER BRIEF",
        "",
        "Operating Status: ACTIVE",
        f"Open Missions: {len(snapshot['open_missions'])}",
        f"Blocked Missions: {len(snapshot['blocked_missions'])}",
        "",
        "Latest SITREP:",
        latest_sitrep.get("top_priority") if latest_sitrep else "No SITREP available.",
        "",
        "Latest AAR Lesson:",
        latest_aar.get("lesson_learned") if latest_aar else "No AAR available.",
        "",
        "Next Recommended Action:",
        snapshot["next_recommended_action"],
    ]

    return {
        "status": "ok",
        "brief": "\n".join(brief_lines),
        "data": snapshot,
    }


@app.get("/api/commander/next-action")
def api_commander_next_action():
    snapshot = _build_commander_snapshot()

    return {
        "status": "ok",
        "next_recommended_action": snapshot["next_recommended_action"],
        "blocked_missions": snapshot["blocked_missions"],
        "high_priority_open": snapshot["high_priority_open"],
    }


@app.get("/api/dashboard/summary")
def api_dashboard_summary():
    snapshot = _build_commander_snapshot()

    return {
        "status": "ok",
        "dashboard": {
            "operating_status": snapshot["operating_status"],
            "counts": {
                "total_missions": len(snapshot["missions"]),
                "open_missions": len(snapshot["open_missions"]),
                "blocked_missions": len(snapshot["blocked_missions"]),
                "high_priority_open": len(snapshot["high_priority_open"]),
                "has_sitrep": snapshot["latest_sitrep"] is not None,
                "has_aar": snapshot["latest_aar"] is not None,
            },
            "next_recommended_action": snapshot["next_recommended_action"],
        },
    }


@app.post("/api/daily/start")
def api_daily_start(payload: dict):
    from backend.sitrep_service import create_sitrep

    sitrep = create_sitrep(
        {
            "top_priority": payload.get("top_priority", "Define today's top priority."),
            "blocker": payload.get("blocker", ""),
            "action_1": payload.get("action_1", ""),
            "action_2": payload.get("action_2", ""),
            "action_3": payload.get("action_3", ""),
        }
    )

    return {
        "status": "started",
        "message": "Daily operating cycle started.",
        "sitrep": sitrep,
        "next_recommended_action": sitrep.get("action_1") or "Execute today's top priority.",
    }


@app.post("/api/daily/closeout")
def api_daily_closeout(payload: dict):
    from backend.aar_service import create_aar

    aar = create_aar(
        {
            "mission": payload.get("mission", "Daily Operations"),
            "what_happened": payload.get("what_happened", ""),
            "what_worked": payload.get("what_worked", ""),
            "what_failed": payload.get("what_failed", ""),
            "lesson_learned": payload.get("lesson_learned", ""),
            "next_action": payload.get("next_action", ""),
        }
    )

    return {
        "status": "closed",
        "message": "Daily operating cycle closed.",
        "aar": aar,
        "next_recommended_action": aar.get("next_action") or "Review today's lesson and plan tomorrow.",
    }


@app.get("/api/daily/history")
def api_daily_history(limit: int = 10):
    from backend.sitrep_service import list_sitreps
    from backend.aar_service import list_aars

    sitreps = list_sitreps(limit=limit)
    aars = list_aars(limit=limit)

    return {
        "status": "ok",
        "history": {
            "sitreps": sitreps,
            "aars": aars,
            "counts": {
                "sitreps": len(sitreps),
                "aars": len(aars),
            },
        },
    }


@app.get("/api/dashboard/missions")
def api_dashboard_missions():
    missions = mission_planner.list_missions()

    open_missions = [
        mission for mission in missions
        if mission.get("status") != "completed"
    ]

    completed_missions = [
        mission for mission in missions
        if mission.get("status") == "completed"
    ]

    blocked_missions = [
        mission for mission in open_missions
        if mission.get("status") == "blocked"
    ]

    return {
        "status": "ok",
        "missions": {
            "all": missions,
            "open": open_missions,
            "completed": completed_missions,
            "blocked": blocked_missions,
            "counts": {
                "total": len(missions),
                "open": len(open_missions),
                "completed": len(completed_missions),
                "blocked": len(blocked_missions),
            },
        },
    }


@app.get("/api/dashboard/daily")
def api_dashboard_daily(limit: int = 5):
    from backend.sitrep_service import list_sitreps
    from backend.aar_service import list_aars

    sitreps = list_sitreps(limit=limit)
    aars = list_aars(limit=limit)

    latest_sitrep = sitreps[0] if sitreps else None
    latest_aar = aars[0] if aars else None

    return {
        "status": "ok",
        "daily": {
            "latest_sitrep": latest_sitrep,
            "latest_aar": latest_aar,
            "recent_sitreps": sitreps,
            "recent_aars": aars,
            "counts": {
                "sitreps": len(sitreps),
                "aars": len(aars),
            },
        },
    }


@app.get("/api/dashboard/health")
def api_dashboard_health():
    snapshot = _build_commander_snapshot()

    has_sitrep = snapshot["latest_sitrep"] is not None
    has_aar = snapshot["latest_aar"] is not None
    blocked_count = len(snapshot["blocked_missions"])

    if blocked_count > 0:
        health_status = "attention_required"
    elif not has_sitrep:
        health_status = "needs_daily_start"
    else:
        health_status = "healthy"

    return {
        "status": "ok",
        "health": {
            "overall": health_status,
            "operating_status": snapshot["operating_status"],
            "has_sitrep": has_sitrep,
            "has_aar": has_aar,
            "blocked_missions": blocked_count,
            "open_missions": len(snapshot["open_missions"]),
            "next_recommended_action": snapshot["next_recommended_action"],
        },
    }


# --- Sprint 01 Core Loop compatibility endpoints ---
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4
from fastapi import HTTPException as _Sprint01HTTPException

_sprint01_daily_briefs = []
_sprint01_missions = {}


def _sprint01_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sprint01_default_daily_brief() -> Dict[str, Any]:
    return {
        "id": "default",
        "date": datetime.now(timezone.utc).date().isoformat(),
        "commander_intent": "Maintain mission focus and execute the core loop.",
        "top_priorities": [],
        "risks": [],
        "opportunities": [],
        "health_status": "not_assessed",
        "business_status": "not_assessed",
        "school_status": "not_assessed",
        "family_status": "not_assessed",
        "next_actions": [],
        "created_at": _sprint01_now(),
    }


@app.get("/api/dashboard")
async def sprint01_dashboard() -> Dict[str, Any]:
    missions = list(_sprint01_missions.values())
    completed_statuses = {"complete", "completed", "done"}
    completed = [
        mission for mission in missions
        if str(mission.get("status", "")).lower() in completed_statuses
    ]
    active = [mission for mission in missions if mission not in completed]

    latest_brief = (
        _sprint01_daily_briefs[-1]
        if _sprint01_daily_briefs
        else _sprint01_default_daily_brief()
    )

    return {
        "status": "operational",
        "missions_summary": {
            "total": len(missions),
            "active": len(active),
            "completed": len(completed),
        },
        "daily_brief": latest_brief,
        "aar_count": 0,
        "judgment_ready": True,
    }


@app.get("/api/daily-brief")
async def sprint01_get_daily_brief() -> Dict[str, Any]:
    brief = (
        _sprint01_daily_briefs[-1]
        if _sprint01_daily_briefs
        else _sprint01_default_daily_brief()
    )
    return {"daily_brief": brief}


@app.post("/api/daily-brief")
async def sprint01_create_daily_brief(payload: Dict[str, Any]) -> Dict[str, Any]:
    brief = _sprint01_default_daily_brief()
    brief.update(payload)
    brief["id"] = str(payload.get("id") or uuid4())
    brief["created_at"] = _sprint01_now()

    _sprint01_daily_briefs.append(brief)
    return {"daily_brief": brief}


@app.post("/missions")
async def sprint01_create_mission(payload: Dict[str, Any]) -> Dict[str, Any]:
    mission_id = str(payload.get("id") or uuid4())

    mission = {
        "id": mission_id,
        "title": payload.get("title", "Untitled mission"),
        "intent": payload.get("intent", ""),
        "priority": payload.get("priority", "medium"),
        "status": payload.get("status", "planned"),
        "risk": payload.get("risk", "not_assessed"),
        "next_action": payload.get("next_action", ""),
        "due_date": payload.get("due_date"),
        "created_at": _sprint01_now(),
        "updated_at": _sprint01_now(),
    }

    _sprint01_missions[mission_id] = mission
    return {"mission": mission}


@app.patch("/missions/{mission_id}")
async def sprint01_update_mission(
    mission_id: str,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    if mission_id not in _sprint01_missions:
        raise _Sprint01HTTPException(status_code=404, detail="Mission not found")

    mission = _sprint01_missions[mission_id]

    allowed_fields = {
        "title",
        "intent",
        "priority",
        "status",
        "risk",
        "next_action",
        "due_date",
    }

    for key, value in payload.items():
        if key in allowed_fields:
            mission[key] = value

    mission["updated_at"] = _sprint01_now()
    _sprint01_missions[mission_id] = mission

    return {"mission": mission}


# --- Sprint 02 Commander UI ---
from fastapi.responses import HTMLResponse as _Sprint02HTMLResponse


@app.get("/api/core/missions")
async def sprint02_list_core_missions() -> Dict[str, Any]:
    return {"missions": list(_sprint01_missions.values())}


@app.get("/command", response_class=_Sprint02HTMLResponse)
async def sprint02_command_ui() -> str:
    return """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Salus Command OS</title>
  <style>
    :root {
      --bg: #07111f;
      --panel: #0d1b2e;
      --panel2: #13243b;
      --gold: #d4af37;
      --text: #f4f7fb;
      --muted: #9fb0c5;
      --danger: #ff6b6b;
      --ok: #3ddc97;
      --border: #223753;
    }

    * {
      box-sizing: border-box;
    }

    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--bg);
      color: var(--text);
    }

    header {
      padding: 18px 24px;
      border-bottom: 1px solid var(--border);
      background: #050c16;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }

    h1 {
      margin: 0;
      color: var(--gold);
      font-size: 24px;
      letter-spacing: 0.04em;
    }

    .sub {
      color: var(--muted);
      font-size: 13px;
      margin-top: 4px;
    }

    main {
      padding: 20px;
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 18px;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 16px;
      box-shadow: 0 8px 18px rgba(0,0,0,0.25);
    }

    .wide {
      grid-column: span 2;
    }

    h2 {
      margin: 0 0 12px 0;
      color: var(--gold);
      font-size: 18px;
    }

    label {
      display: block;
      margin-top: 10px;
      color: var(--muted);
      font-size: 13px;
    }

    input, textarea, select {
      width: 100%;
      margin-top: 5px;
      padding: 10px;
      background: var(--panel2);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 8px;
      font-size: 14px;
    }

    textarea {
      min-height: 80px;
    }

    button {
      margin-top: 12px;
      padding: 10px 14px;
      background: var(--gold);
      border: none;
      color: #0a0f18;
      font-weight: bold;
      border-radius: 8px;
      cursor: pointer;
    }

    button.secondary {
      background: var(--panel2);
      color: var(--text);
      border: 1px solid var(--border);
      margin-right: 8px;
    }

    pre {
      background: #050c16;
      padding: 12px;
      border-radius: 8px;
      overflow: auto;
      color: #dce7f5;
      border: 1px solid var(--border);
      max-height: 320px;
    }

    .mission {
      border: 1px solid var(--border);
      background: var(--panel2);
      border-radius: 10px;
      padding: 12px;
      margin-bottom: 10px;
    }

    .mission-title {
      font-weight: bold;
      color: var(--text);
    }

    .mission-meta {
      color: var(--muted);
      font-size: 13px;
      margin-top: 5px;
    }

    .badge {
      display: inline-block;
      padding: 3px 8px;
      border-radius: 999px;
      background: #1c3353;
      color: var(--text);
      font-size: 12px;
      margin-right: 6px;
    }

    .ok {
      color: var(--ok);
    }

    .danger {
      color: var(--danger);
    }

    @media (max-width: 900px) {
      main {
        grid-template-columns: 1fr;
      }

      .wide {
        grid-column: span 1;
      }
    }
  </style>
</head>
<body>
  <header>
    <div>
      <h1>Salus Command OS</h1>
      <div class="sub">Sprint 02 — Local Commander Dashboard UI</div>
    </div>
    <div class="sub">Human in command. AI as force multiplier.</div>
  </header>

  <main>
    <section class="panel">
      <h2>Commander Dashboard</h2>
      <button onclick="loadAll()">Refresh Dashboard</button>
      <pre id="dashboard">Loading...</pre>
    </section>

    <section class="panel">
      <h2>Daily Commander Brief</h2>
      <label>Commander Intent</label>
      <textarea id="brief_intent">Use Project Salus daily.</textarea>

      <label>Top Priorities, one per line</label>
      <textarea id="brief_priorities">Test UI
Prepare Sprint 02
Avoid scope creep</textarea>

      <label>Risks, one per line</label>
      <textarea id="brief_risks">Scope creep
Tool distraction</textarea>

      <label>Next Actions, one per line</label>
      <textarea id="brief_actions">Create mission
Run tests
Commit checkpoint</textarea>

      <button onclick="createBrief()">Save Daily Brief</button>
      <pre id="brief_result">No brief saved yet.</pre>
    </section>

    <section class="panel">
      <h2>Create Mission</h2>
      <label>Title</label>
      <input id="mission_title" value="Sprint 02 Dashboard UI" />

      <label>Intent</label>
      <textarea id="mission_intent">Create usable visual command dashboard.</textarea>

      <label>Priority</label>
      <select id="mission_priority">
        <option>high</option>
        <option>medium</option>
        <option>low</option>
      </select>

      <label>Status</label>
      <select id="mission_status">
        <option>planned</option>
        <option>in_progress</option>
        <option>blocked</option>
        <option>completed</option>
      </select>

      <label>Risk</label>
      <select id="mission_risk">
        <option>low</option>
        <option>medium</option>
        <option>high</option>
      </select>

      <label>Next Action</label>
      <input id="mission_next_action" value="Define UI scope" />

      <button onclick="createMission()">Create Mission</button>
      <pre id="mission_result">No mission created yet.</pre>
    </section>

    <section class="panel">
      <h2>Active Missions</h2>
      <button onclick="loadMissions()">Refresh Missions</button>
      <div id="missions">Loading...</div>
    </section>

    <section class="panel wide">
      <h2>Sprint Guardrails</h2>
      <pre>
DO BUILD:
- Dashboard summary
- Daily brief view/create
- Mission create/list/update
- Basic local usability

DO NOT BUILD YET:
- Agent fleets
- Supabase
- Vector DB
- Multi-user
- Public product
- Payments
- Enterprise portal
- Frontend polish rabbit hole
      </pre>
    </section>
  </main>

  <script>
    function lines(id) {
      return document.getElementById(id).value
        .split("\\n")
        .map(x => x.trim())
        .filter(Boolean);
    }

    async function jsonFetch(url, options = {}) {
      const response = await fetch(url, options);
      const text = await response.text();

      try {
        return JSON.parse(text);
      } catch {
        return { raw: text, status: response.status };
      }
    }

    async function loadDashboard() {
      const data = await jsonFetch("/api/dashboard");
      document.getElementById("dashboard").textContent = JSON.stringify(data, null, 2);
    }

    async function createBrief() {
      const payload = {
        commander_intent: document.getElementById("brief_intent").value,
        top_priorities: lines("brief_priorities"),
        risks: lines("brief_risks"),
        next_actions: lines("brief_actions")
      };

      const data = await jsonFetch("/api/daily-brief", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
      });

      document.getElementById("brief_result").textContent = JSON.stringify(data, null, 2);
      await loadDashboard();
    }

    async function createMission() {
      const payload = {
        title: document.getElementById("mission_title").value,
        intent: document.getElementById("mission_intent").value,
        priority: document.getElementById("mission_priority").value,
        status: document.getElementById("mission_status").value,
        risk: document.getElementById("mission_risk").value,
        next_action: document.getElementById("mission_next_action").value
      };

      const data = await jsonFetch("/missions", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
      });

      document.getElementById("mission_result").textContent = JSON.stringify(data, null, 2);
      await loadAll();
    }

    async function updateMission(id, status) {
      await jsonFetch(`/missions/${id}`, {
        method: "PATCH",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({status: status})
      });

      await loadAll();
    }

    function missionHtml(mission) {
      return `
        <div class="mission">
          <div class="mission-title">${mission.title || "Untitled mission"}</div>
          <div class="mission-meta">
            <span class="badge">Status: ${mission.status}</span>
            <span class="badge">Priority: ${mission.priority}</span>
            <span class="badge">Risk: ${mission.risk}</span>
          </div>
          <div class="mission-meta">Intent: ${mission.intent || ""}</div>
          <div class="mission-meta">Next action: ${mission.next_action || ""}</div>
          <button class="secondary" onclick="updateMission('${mission.id}', 'in_progress')">Mark In Progress</button>
          <button class="secondary" onclick="updateMission('${mission.id}', 'completed')">Mark Complete</button>
        </div>
      `;
    }

    async function loadMissions() {
      const data = await jsonFetch("/api/core/missions");
      const missions = data.missions || [];

      document.getElementById("missions").innerHTML =
        missions.length
          ? missions.map(missionHtml).join("")
          : "<div class='mission-meta'>No missions yet.</div>";
    }

    async function loadAll() {
      await loadDashboard();
      await loadMissions();
    }

    loadAll();
  </script>
</body>
</html>
    """
