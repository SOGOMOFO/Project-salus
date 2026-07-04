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
async def sprint03_command_page():
    html = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Salus Command OS</title>
  <style>
    :root {
      --bg: #07111f;
      --panel: #0f1b2d;
      --panel-2: #13243a;
      --gold: #d8a735;
      --text: #f4f7fb;
      --muted: #a8b3c5;
      --danger: #ff6b6b;
      --ok: #64d28a;
      --border: #263954;
    }

    body {
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--bg);
      color: var(--text);
    }

    header {
      padding: 24px 32px;
      border-bottom: 1px solid var(--border);
      background: #050b14;
    }

    h1 {
      margin: 0;
      color: var(--gold);
      letter-spacing: 0.5px;
    }

    h2 {
      color: var(--gold);
      margin-top: 0;
    }

    .sub {
      color: var(--muted);
      margin-top: 8px;
    }

    main {
      padding: 24px;
      display: grid;
      grid-template-columns: repeat(2, minmax(320px, 1fr));
      gap: 18px;
    }

    .panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 18px;
      box-shadow: 0 8px 20px rgba(0,0,0,0.25);
    }

    .wide {
      grid-column: 1 / -1;
    }

    label {
      display: block;
      margin-top: 12px;
      color: var(--muted);
      font-size: 14px;
    }

    input, textarea, select {
      width: 100%;
      box-sizing: border-box;
      margin-top: 6px;
      padding: 10px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--panel-2);
      color: var(--text);
    }

    textarea {
      min-height: 80px;
    }

    button {
      margin-top: 14px;
      padding: 10px 14px;
      border-radius: 8px;
      border: 1px solid var(--gold);
      background: var(--gold);
      color: #08111e;
      font-weight: 700;
      cursor: pointer;
    }

    button.secondary {
      background: transparent;
      color: var(--gold);
    }

    pre {
      white-space: pre-wrap;
      word-break: break-word;
      background: #07101d;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      color: var(--text);
      max-height: 360px;
      overflow: auto;
    }

    .status {
      margin-top: 10px;
      color: var(--muted);
      font-size: 14px;
    }

    .ok {
      color: var(--ok);
    }

    .error {
      color: var(--danger);
    }

    .mission-card, .aar-card {
      background: #07101d;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px;
      margin-top: 10px;
    }

    .mission-title {
      color: var(--gold);
      font-weight: 700;
    }

    .small {
      color: var(--muted);
      font-size: 13px;
    }
  </style>
</head>

<body>
  <header>
    <h1>Salus Command OS</h1>
    <div class="sub">Sprint 03 — Local Command Loop UI</div>
  </header>

  <main>
    <section class="panel wide">
      <h2>Commander Dashboard</h2>
      <button onclick="loadAll()">Refresh Dashboard</button>
      <div id="global_status" class="status">Ready.</div>
      <pre id="dashboard">Loading dashboard...</pre>
    </section>

    <section class="panel">
      <h2>Daily Commander Brief</h2>

      <label>Commander Intent</label>
      <textarea id="brief_intent">Use Project Salus daily and complete the command loop.</textarea>

      <label>Top Priorities</label>
      <input id="brief_priorities" value="Test UI, Create mission, Enter AAR" />

      <label>Risks</label>
      <input id="brief_risks" value="Scope creep, Tool distraction" />

      <label>Next Actions</label>
      <input id="brief_actions" value="Run smoke test, Commit checkpoint" />

      <button onclick="saveBrief()">Save Daily Brief</button>
      <pre id="brief_result">No brief saved yet.</pre>
    </section>

    <section class="panel">
      <h2>Create Mission</h2>

      <label>Title</label>
      <input id="mission_title" value="Sprint 03 Mission/AAR UI" />

      <label>Intent</label>
      <textarea id="mission_intent">Complete the browser-based command loop.</textarea>

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
      <input id="mission_next_action" value="Create AAR form" />

      <label>Due Date</label>
      <input id="mission_due_date" value="2026-07-31" />

      <button onclick="createMission()">Create Mission</button>
      <pre id="mission_result">No mission created yet.</pre>
    </section>

    <section class="panel wide">
      <h2>Active Missions</h2>
      <button onclick="loadMissions()">Refresh Missions</button>
      <div id="missions">Loading missions...</div>
    </section>

    <section class="panel">
      <h2>Update Mission</h2>

      <label>Mission ID</label>
      <input id="update_mission_id" placeholder="Paste mission id from Active Missions" />

      <label>Status</label>
      <select id="update_status">
        <option>planned</option>
        <option>in_progress</option>
        <option>blocked</option>
        <option>completed</option>
      </select>

      <label>Priority</label>
      <select id="update_priority">
        <option>high</option>
        <option>medium</option>
        <option>low</option>
      </select>

      <label>Risk</label>
      <select id="update_risk">
        <option>low</option>
        <option>medium</option>
        <option>high</option>
      </select>

      <label>Next Action</label>
      <input id="update_next_action" value="Run tests and commit" />

      <button onclick="updateMission()">Update Mission</button>
      <pre id="update_result">No mission updated yet.</pre>
    </section>

    <section class="panel">
      <h2>AAR Entry</h2>

      <label>What Happened</label>
      <textarea id="aar_what_happened">Built and tested the next Project Salus command loop step.</textarea>

      <label>What Worked</label>
      <textarea id="aar_what_worked">Small sprint scope and test gates kept the build controlled.</textarea>

      <label>What Failed</label>
      <textarea id="aar_what_failed">Tool/API key issues slowed AI coding assistance.</textarea>

      <label>Lesson Learned</label>
      <textarea id="aar_lesson_learned">Manual patching is a reliable fallback when AI tooling blocks execution.</textarea>

      <label>Adjustment</label>
      <textarea id="aar_adjustment">Use batch-mode patches and tests for faster progress.</textarea>

      <button onclick="saveAAR()">Save AAR</button>
      <pre id="aar_result">No AAR saved yet.</pre>
    </section>

    <section class="panel wide">
      <h2>AAR Log</h2>
      <button onclick="loadAARs()">Refresh AARs</button>
      <div id="aars">Loading AARs...</div>
    </section>

    <section class="panel wide">
      <h2>Sprint Guardrails</h2>
      <pre>
DO BUILD:
- Mission creation
- Mission update
- AAR entry
- AAR display
- Dashboard refresh
- Basic success/error messages

DO NOT BUILD:
- Login
- Multi-user support
- Supabase
- Agent orchestration
- Public deployment
- Mobile app
      </pre>
    </section>
  </main>

  <script>
    function showStatus(message, ok = true) {
      const el = document.getElementById("global_status");
      el.textContent = message;
      el.className = ok ? "status ok" : "status error";
    }

    async function api(path, options = {}) {
      const response = await fetch(path, {
        headers: {"Content-Type": "application/json"},
        ...options
      });

      let data;
      try {
        data = await response.json();
      } catch {
        data = {raw: await response.text()};
      }

      if (!response.ok) {
        throw new Error(JSON.stringify(data));
      }

      return data;
    }

    async function loadDashboard() {
      const data = await api("/api/dashboard");
      document.getElementById("dashboard").textContent = JSON.stringify(data, null, 2);
      return data;
    }

    async function saveBrief() {
      try {
        const payload = {
          commander_intent: document.getElementById("brief_intent").value,
          top_priorities: document.getElementById("brief_priorities").value.split(",").map(x => x.trim()).filter(Boolean),
          risks: document.getElementById("brief_risks").value.split(",").map(x => x.trim()).filter(Boolean),
          next_actions: document.getElementById("brief_actions").value.split(",").map(x => x.trim()).filter(Boolean)
        };

        const data = await api("/api/daily-brief", {
          method: "POST",
          body: JSON.stringify(payload)
        });

        document.getElementById("brief_result").textContent = JSON.stringify(data, null, 2);
        showStatus("Daily brief saved.");
        await loadDashboard();
      } catch (err) {
        showStatus("Daily brief save failed: " + err.message, false);
      }
    }

    async function createMission() {
      try {
        const payload = {
          title: document.getElementById("mission_title").value,
          intent: document.getElementById("mission_intent").value,
          priority: document.getElementById("mission_priority").value,
          status: document.getElementById("mission_status").value,
          risk: document.getElementById("mission_risk").value,
          next_action: document.getElementById("mission_next_action").value,
          due_date: document.getElementById("mission_due_date").value
        };

        const data = await api("/api/missions", {
          method: "POST",
          body: JSON.stringify(payload)
        });

        document.getElementById("mission_result").textContent = JSON.stringify(data, null, 2);
        document.getElementById("update_mission_id").value = data.mission.id;
        showStatus("Mission created.");
        await loadMissions();
        await loadDashboard();
      } catch (err) {
        showStatus("Mission creation failed: " + err.message, false);
      }
    }

    async function loadMissions() {
      try {
        const data = await api("/api/missions");
        const missions = data.missions || [];
        const container = document.getElementById("missions");

        if (!missions.length) {
          container.innerHTML = "<div class='small'>No missions yet.</div>";
          return;
        }

        container.innerHTML = missions.map(m => `
          <div class="mission-card">
            <div class="mission-title">${m.title || "Untitled Mission"}</div>
            <div class="small">ID: ${m.id}</div>
            <div>Status: ${m.status || ""} | Priority: ${m.priority || ""} | Risk: ${m.risk || ""}</div>
            <div>Intent: ${m.intent || ""}</div>
            <div>Next Action: ${m.next_action || ""}</div>
            <button class="secondary" onclick="selectMission('${m.id}', '${m.status || ""}', '${m.priority || ""}', '${m.risk || ""}', '${(m.next_action || "").replace(/'/g, "\\'")}')">Select for Update</button>
          </div>
        `).join("");
      } catch (err) {
        document.getElementById("missions").innerHTML = "<div class='error'>Mission load failed: " + err.message + "</div>";
      }
    }

    function selectMission(id, status, priority, risk, nextAction) {
      document.getElementById("update_mission_id").value = id;
      if (status) document.getElementById("update_status").value = status;
      if (priority) document.getElementById("update_priority").value = priority;
      if (risk) document.getElementById("update_risk").value = risk;
      document.getElementById("update_next_action").value = nextAction || "";
      showStatus("Mission selected for update.");
    }

    async function updateMission() {
      try {
        const id = document.getElementById("update_mission_id").value.trim();

        if (!id) {
          throw new Error("Mission ID required.");
        }

        const payload = {
          status: document.getElementById("update_status").value,
          priority: document.getElementById("update_priority").value,
          risk: document.getElementById("update_risk").value,
          next_action: document.getElementById("update_next_action").value
        };

        const data = await api(`/api/missions/${id}`, {
          method: "PATCH",
          body: JSON.stringify(payload)
        });

        document.getElementById("update_result").textContent = JSON.stringify(data, null, 2);
        showStatus("Mission updated.");
        await loadMissions();
        await loadDashboard();
      } catch (err) {
        showStatus("Mission update failed: " + err.message, false);
      }
    }

    async function saveAAR() {
      try {
        const payload = {
          what_happened: document.getElementById("aar_what_happened").value,
          what_worked: document.getElementById("aar_what_worked").value,
          what_failed: document.getElementById("aar_what_failed").value,
          lesson_learned: document.getElementById("aar_lesson_learned").value,
          adjustment: document.getElementById("aar_adjustment").value
        };

        const data = await api("/api/aar", {
          method: "POST",
          body: JSON.stringify(payload)
        });

        document.getElementById("aar_result").textContent = JSON.stringify(data, null, 2);
        showStatus("AAR saved.");
        await loadAARs();
        await loadDashboard();
      } catch (err) {
        showStatus("AAR save failed: " + err.message, false);
      }
    }

    async function loadAARs() {
      try {
        const data = await api("/api/aar");
        const list = data.aars || data.aar_log || data.items || data || [];
        const aars = Array.isArray(list) ? list : [list];
        const container = document.getElementById("aars");

        if (!aars.length) {
          container.innerHTML = "<div class='small'>No AARs yet.</div>";
          return;
        }

        container.innerHTML = aars.map(a => `
          <div class="aar-card">
            <div class="mission-title">${a.title || a.date || a.id || "AAR"}</div>
            <div>What Happened: ${a.what_happened || a.summary || ""}</div>
            <div>Lesson Learned: ${a.lesson_learned || a.lesson || ""}</div>
            <div>Adjustment: ${a.adjustment || a.next_action || ""}</div>
          </div>
        `).join("");
      } catch (err) {
        document.getElementById("aars").innerHTML = "<div class='error'>AAR load failed: " + err.message + "</div>";
      }
    }

    async function loadAll() {
      try {
        await loadDashboard();
        await loadMissions();
        await loadAARs();
        showStatus("Dashboard refreshed.");
      } catch (err) {
        showStatus("Refresh failed: " + err.message, false);
      }
    }

    loadAll();
  </script>
</body>
</html>
"""
    return _Sprint02HTMLResponse(content=html)

@app.get("/api/missions")
async def sprint03_list_missions() -> Dict[str, Any]:
    """Local UI compatibility endpoint for listing Sprint 01 missions."""
    return {"missions": list(_sprint01_missions.values())}


@app.post("/api/missions")
async def sprint03_create_mission(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Local UI compatibility endpoint for creating Sprint 01 missions."""
    return await sprint01_create_mission(payload)


@app.patch("/api/missions/{mission_id}")
async def sprint03_update_mission(mission_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Local UI compatibility endpoint for updating Sprint 01 missions."""
    return await sprint01_update_mission(mission_id, payload)
