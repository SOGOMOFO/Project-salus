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
from backend.routers.family import router as family_router
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
app.include_router(family_router)


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

from backend.routes import operator_console as _operator_console_router
app.include_router(_operator_console_router.router)


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
        (
            latest_aar.get("lesson_learned")
            or latest_aar.get("lesson")
            or "No AAR lesson captured."
        ) if latest_aar else "No AAR available.",
        "",
        "Next Recommended Action:",
        snapshot["next_recommended_action"],
    ]

    return {
        "status": "ok",
        "brief": "\n".join(str(line) if line is not None else "" for line in brief_lines),
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

# --- Sprint 04 Local JSON Persistence ---
import json as _sprint04_json
from pathlib import Path as _Sprint04Path

_sprint04_data_dir = _Sprint04Path("data")
_sprint04_data_dir.mkdir(exist_ok=True)

_sprint04_daily_briefs_file = _sprint04_data_dir / "salus_daily_briefs.json"
_sprint04_missions_file = _sprint04_data_dir / "salus_missions.json"
_sprint04_aars_file = _sprint04_data_dir / "salus_aars.json"


def _sprint04_read_json(path, default):
    try:
        if path.exists():
            return _sprint04_json.loads(path.read_text())
    except Exception:
        return default
    return default


def _sprint04_write_json(path, data):
    path.write_text(_sprint04_json.dumps(data, indent=2, sort_keys=True, default=str))


_sprint01_daily_briefs = _sprint04_read_json(_sprint04_daily_briefs_file, [])
_sprint01_missions = _sprint04_read_json(_sprint04_missions_file, {})
_sprint04_aars = _sprint04_read_json(_sprint04_aars_file, [])


def _sprint04_save_daily_briefs():
    _sprint04_write_json(_sprint04_daily_briefs_file, _sprint01_daily_briefs)


def _sprint04_save_missions():
    _sprint04_write_json(_sprint04_missions_file, _sprint01_missions)


def _sprint04_save_aars():
    _sprint04_write_json(_sprint04_aars_file, _sprint04_aars)



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
        "aar_count": len(globals().get("_sprint04_aars", [])) or len(_sprint01_load_json(_SPRINT01_AARS_FILE, [])),
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
    _sprint04_save_daily_briefs()
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
    _sprint04_save_missions()
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
    _sprint04_save_missions()

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


# --- Sprint 04 Persistent AAR Override ---
# Remove older /api/aar route handlers so local JSON persistence is authoritative.
app.router.routes = [
    route for route in app.router.routes
    if not (
        getattr(route, "path", "") in {"/api/aar", "/api/aar/{aar_id}"}
        and bool(getattr(route, "methods", set()) & {"GET", "POST"})
    )
]


@app.post("/api/aar")
async def sprint04_create_aar(payload: Dict[str, Any]) -> Dict[str, Any]:
    aar_id = str(payload.get("id") or uuid4())
    record = {
        "id": aar_id,
        "date": payload.get("date") or datetime.now(timezone.utc).date().isoformat(),
        "title": payload.get("title", "Project Salus AAR"),
        "what_happened": payload.get("what_happened", payload.get("summary", "")),
        "what_worked": payload.get("what_worked", ""),
        "what_failed": payload.get("what_failed", ""),
        "lesson_learned": payload.get("lesson_learned", payload.get("lesson", "")),
        "adjustment": payload.get("adjustment", payload.get("next_action", "")),
        "created_at": _sprint01_now(),
    }

    # Preserve additional caller-provided fields without overwriting core fields.
    for key, value in payload.items():
        record.setdefault(key, value)

    _sprint04_aars.append(record)
    _sprint04_save_aars()

    return {
        "status": "ok",
        "aar_id": aar_id,
        "aar": record,
    }


@app.get("/api/aar")
async def sprint04_list_aars() -> Dict[str, Any]:
    return {"status": "ok", "aars": _sprint04_aars,
        "aar_log": _sprint04_aars,
        "items": _sprint04_aars,
        "count": len(_sprint04_aars),
    }


@app.get("/api/aar/{aar_id}")
async def sprint04_get_aar(aar_id: str) -> Dict[str, Any]:
    for record in _sprint04_aars:
        if str(record.get("id")) == str(aar_id):
            return {"status": "ok", "aar": record}

    raise _Sprint01HTTPException(status_code=404, detail="AAR not found")


# --- Sprint 05 Mission/Data Contract compatibility endpoints ---
@app.get("/api/missions")
async def sprint05_list_missions():
    """Public Sprint 05 mission list contract.

    Keeps legacy GET /missions behavior untouched.
    """
    missions = list(_sprint01_missions.values())
    return {
        "status": "ok",
        "count": len(missions),
        "missions": missions,
    }


# --- Sprint compatibility JSON helpers ---
from pathlib import Path as _SprintPath
import json as _sprint_json

_SPRINT_DATA_DIR = _SprintPath("data")
_SPRINT_DATA_DIR.mkdir(exist_ok=True)
_SPRINT01_AARS_FILE = "sprint04_aars.json"


def _sprint01_load_json(filename, default=None):
    """Load Sprint JSON data safely."""
    path = _SPRINT_DATA_DIR / filename
    if default is None:
        default = []
    if not path.exists():
        return default
    try:
        return _sprint_json.loads(path.read_text())
    except Exception:
        return default


def _sprint01_save_json(filename, data):
    """Save Sprint JSON data safely."""
    path = _SPRINT_DATA_DIR / filename
    path.write_text(_sprint_json.dumps(data, indent=2, default=str))
    return data


# --- Sprint 05 route priority fix ---
def _sprint05_prioritize_api_missions_route() -> None:
    target_route = None

    for route in list(app.router.routes):
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", set())
        endpoint = getattr(route, "endpoint", None)
        endpoint_name = getattr(endpoint, "__name__", "")

        if path == "/api/missions" and "GET" in methods and endpoint_name == "sprint05_list_missions":
            target_route = route
            break

    if target_route is None:
        return

    app.router.routes.remove(target_route)

    for index, route in enumerate(app.router.routes):
        path = getattr(route, "path", None)
        methods = getattr(route, "methods", set())

        if path == "/api/missions" and "GET" in methods:
            app.router.routes.insert(index, target_route)
            return

    app.router.routes.append(target_route)


_sprint05_prioritize_api_missions_route()



# --- Sprint 06 Data Hygiene and Reset Controls ---
@app.post("/api/dev/reset")
async def sprint06_dev_reset(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Local development reset for Sprint runtime data.

    This endpoint is intentionally guarded by a confirmation phrase.
    It is for local/dev/test use only and should not be exposed as a production admin feature.
    """
    confirmation = str(payload.get("confirmation", "")).strip()

    if confirmation != "RESET_PROJECT_SALUS_DEV_DATA":
        raise _Sprint01HTTPException(
            status_code=400,
            detail="Reset confirmation required.",
        )

    # Clear in-memory Sprint runtime stores when present.
    if "_sprint01_daily_briefs" in globals():
        _sprint01_daily_briefs.clear()

    if "_sprint01_missions" in globals():
        _sprint01_missions.clear()

    if "_sprint04_aars" in globals():
        _sprint04_aars.clear()

    # Clear known runtime persistence files when helper functions exist.
    cleared_files = []

    known_files = [
        "sprint01_daily_briefs.json",
        "sprint01_missions.json",
        "sprint04_missions.json",
        "sprint04_aars.json",
    ]

    save_json = globals().get("_sprint01_save_json")

    if save_json:
        for filename in known_files:
            try:
                save_json(filename, [])
                cleared_files.append(filename)
            except Exception:
                pass

    # Sprint 12 capability data reset
    sprint12_memory_lists = [
        "_schoolhouse_courses",
        "_schoolhouse_study_sessions",
        "_schoolhouse_wrong_answer_reviews",
        "_schoolhouse_writing_tasks",
        "_charisma_self_assessments",
        "_charisma_conversation_aars",
    ]

    for list_name in sprint12_memory_lists:
        value = globals().get(list_name)
        if isinstance(value, list):
            value.clear()
            cleared_files.append(list_name.lstrip("_"))

    sprint12_files = [
        "sprint12_schoolhouse_courses.json",
        "sprint12_schoolhouse_study_sessions.json",
        "sprint12_schoolhouse_wrong_answer_reviews.json",
        "sprint12_schoolhouse_writing_tasks.json",
        "sprint12_charisma_self_assessments.json",
        "sprint12_charisma_conversation_aars.json",
    ]

    for filename in sprint12_files:
        try:
            _sprint01_save_json(filename, [])
            cleared_files.append(filename)
        except Exception:
            pass

    return {
        "status": "ok",
        "reset": True,
        "cleared": {
            "daily_briefs": True,
            "missions": True,
            "aars": True,
            "files": cleared_files,
        },
    }



# --- Sprint 07 Real Daily Use Mode ---
from fastapi.responses import HTMLResponse as _Sprint07HTMLResponse


def _sprint07_latest_brief() -> Dict[str, Any]:
    if "_sprint01_daily_briefs" in globals() and _sprint01_daily_briefs:
        return _sprint01_daily_briefs[-1]
    return _sprint01_default_daily_brief()


def _sprint07_mission_summary() -> Dict[str, Any]:
    missions = list(globals().get("_sprint01_missions", {}).values())
    completed_statuses = {"complete", "completed", "done"}
    blocked_statuses = {"blocked", "stuck"}

    completed = [
        mission for mission in missions
        if str(mission.get("status", "")).lower() in completed_statuses
    ]

    blocked = [
        mission for mission in missions
        if str(mission.get("status", "")).lower() in blocked_statuses
    ]

    active = [
        mission for mission in missions
        if mission not in completed
    ]

    return {
        "total": len(missions),
        "active": len(active),
        "completed": len(completed),
        "blocked": len(blocked),
    }


def _sprint07_aar_count() -> int:
    live_aars = globals().get("_sprint04_aars", [])
    if live_aars:
        return len(live_aars)

    try:
        return len(_sprint01_load_json(_SPRINT01_AARS_FILE, []))
    except Exception:
        return 0


@app.get("/api/daily-use/state")
async def sprint07_daily_use_state() -> Dict[str, Any]:
    missions = list(globals().get("_sprint01_missions", {}).values())

    return {
        "status": "ok",
        "mode": "real_daily_use",
        "daily_brief": _sprint07_latest_brief(),
        "missions_summary": _sprint07_mission_summary(),
        "missions": missions,
        "aar_count": _sprint07_aar_count(),
        "ready": True,
        "next_required_action": "Run morning brief, update missions, and close with an AAR.",
    }


@app.post("/api/daily-use/brief")
async def sprint07_create_daily_use_brief(payload: Dict[str, Any]) -> Dict[str, Any]:
    brief = _sprint01_default_daily_brief()
    brief.update(payload)
    brief["id"] = str(payload.get("id") or uuid4())
    brief["mode"] = "real_daily_use"
    brief["created_at"] = _sprint01_now()

    _sprint01_daily_briefs.append(brief)

    save_json = globals().get("_sprint01_save_json")
    if save_json:
        try:
            save_json("sprint01_daily_briefs.json", _sprint01_daily_briefs)
        except Exception:
            pass

    return {
        "status": "ok",
        "daily_brief": brief,
    }


@app.post("/api/daily-use/aar")
async def sprint07_create_daily_use_aar(payload: Dict[str, Any]) -> Dict[str, Any]:
    record = {
        "id": str(payload.get("id") or uuid4()),
        "date": payload.get("date") or datetime.now(timezone.utc).date().isoformat(),
        "mode": "real_daily_use",
        "what_happened": payload.get("what_happened", ""),
        "what_worked": payload.get("what_worked", ""),
        "what_failed": payload.get("what_failed", ""),
        "lesson_learned": payload.get("lesson_learned", ""),
        "adjustment": payload.get("adjustment", ""),
        "created_at": _sprint01_now(),
    }

    if "_sprint04_aars" not in globals():
        globals()["_sprint04_aars"] = []

    _sprint04_aars.append(record)

    save_json = globals().get("_sprint01_save_json")
    if save_json:
        try:
            save_json(_SPRINT01_AARS_FILE, _sprint04_aars)
        except Exception:
            pass

    return {
        "status": "ok",
        "aar": record,
    }


@app.get("/command/daily", response_class=_Sprint07HTMLResponse)
async def sprint07_daily_command_page() -> _Sprint07HTMLResponse:
    html = """
    <!doctype html>
    <html>
      <head>
        <title>Project Salus — Real Daily Use Mode</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            background: #07111f;
            color: #f4f7fb;
            margin: 0;
            padding: 32px;
          }
          h1, h2 {
            color: #d7b46a;
          }
          .panel {
            border: 1px solid #28405f;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 18px;
            background: #0d1c2f;
          }
          button {
            background: #d7b46a;
            border: none;
            padding: 10px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
          }
          textarea, input, select {
            width: 100%;
            margin: 6px 0 12px 0;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #28405f;
            background: #081525;
            color: #f4f7fb;
          }
          pre {
            white-space: pre-wrap;
            background: #081525;
            padding: 14px;
            border-radius: 8px;
            border: 1px solid #28405f;
          }
        </style>
      </head>
      <body>
        <h1>Project Salus — Real Daily Use Mode</h1>

        <div class="panel">
          <h2>Dashboard State</h2>
          <button onclick="refreshState()">Refresh State</button>
          <pre id="state">Ready.</pre>
        </div>

        <div class="panel">
          <h2>Morning Commander Brief</h2>
          <input id="intent" placeholder="Commander intent" value="Execute today's highest-leverage missions.">
          <textarea id="priorities" placeholder="Top priorities, one per line"></textarea>
          <textarea id="risks" placeholder="Risks, one per line"></textarea>
          <textarea id="actions" placeholder="Next actions, one per line"></textarea>
          <button onclick="saveBrief()">Save Daily Brief</button>
        </div>

        <div class="panel">
          <h2>Mission Entry</h2>
          <input id="mission_title" placeholder="Mission title">
          <textarea id="mission_intent" placeholder="Mission intent"></textarea>
          <select id="mission_priority">
            <option>high</option>
            <option>medium</option>
            <option>low</option>
          </select>
          <select id="mission_status">
            <option>planned</option>
            <option>in_progress</option>
            <option>blocked</option>
            <option>completed</option>
          </select>
          <input id="mission_next_action" placeholder="Next action">
          <button onclick="createMission()">Create Mission</button>
        </div>

        <div class="panel">
          <h2>Evening AAR</h2>
          <textarea id="what_happened" placeholder="What happened?"></textarea>
          <textarea id="what_worked" placeholder="What worked?"></textarea>
          <textarea id="what_failed" placeholder="What failed?"></textarea>
          <textarea id="lesson" placeholder="Lesson learned"></textarea>
          <textarea id="adjustment" placeholder="Adjustment"></textarea>
          <button onclick="saveAAR()">Save AAR</button>
        </div>

        <script>
          async function api(path, options = {}) {
            const res = await fetch(path, {
              headers: { "Content-Type": "application/json" },
              ...options
            });
            return await res.json();
          }

          function lines(id) {
            return document.getElementById(id).value
              .split("\\n")
              .map(x => x.trim())
              .filter(Boolean);
          }

          async function refreshState() {
            const data = await api("/api/daily-use/state");
            document.getElementById("state").textContent = JSON.stringify(data, null, 2);
          }

          async function saveBrief() {
            await api("/api/daily-use/brief", {
              method: "POST",
              body: JSON.stringify({
                commander_intent: document.getElementById("intent").value,
                top_priorities: lines("priorities"),
                risks: lines("risks"),
                next_actions: lines("actions")
              })
            });
            await refreshState();
          }

          async function createMission() {
            await api("/missions", {
              method: "POST",
              body: JSON.stringify({
                title: document.getElementById("mission_title").value,
                intent: document.getElementById("mission_intent").value,
                priority: document.getElementById("mission_priority").value,
                status: document.getElementById("mission_status").value,
                risk: "not_assessed",
                next_action: document.getElementById("mission_next_action").value
              })
            });
            await refreshState();
          }

          async function saveAAR() {
            await api("/api/daily-use/aar", {
              method: "POST",
              body: JSON.stringify({
                what_happened: document.getElementById("what_happened").value,
                what_worked: document.getElementById("what_worked").value,
                what_failed: document.getElementById("what_failed").value,
                lesson_learned: document.getElementById("lesson").value,
                adjustment: document.getElementById("adjustment").value
              })
            });
            await refreshState();
          }

          refreshState();
        </script>
      </body>
    </html>
    """
    return _Sprint07HTMLResponse(content=html)



# --- Sprint 08 Schoolhouse Learning Coach Module ---
_SPRINT12_SCHOOLHOUSE_COURSES_FILE = "sprint12_schoolhouse_courses.json"
_SPRINT12_SCHOOLHOUSE_STUDY_SESSIONS_FILE = "sprint12_schoolhouse_study_sessions.json"
_SPRINT12_SCHOOLHOUSE_WRONG_ANSWER_REVIEWS_FILE = "sprint12_schoolhouse_wrong_answer_reviews.json"
_SPRINT12_SCHOOLHOUSE_WRITING_TASKS_FILE = "sprint12_schoolhouse_writing_tasks.json"
_SPRINT12_CHARISMA_SELF_ASSESSMENTS_FILE = "sprint12_charisma_self_assessments.json"
_SPRINT12_CHARISMA_CONVERSATION_AARS_FILE = "sprint12_charisma_conversation_aars.json"


def _sprint12_load_list(filename: str) -> list:
    try:
        return _sprint01_load_json(filename, [])
    except Exception:
        return []


def _sprint12_save_list(filename: str, data: list) -> None:
    try:
        _sprint01_save_json(filename, data)
    except Exception:
        pass


def _sprint12_save_capability_data() -> None:
    _sprint12_save_list(_SPRINT12_SCHOOLHOUSE_COURSES_FILE, globals().get("_schoolhouse_courses", []))
    _sprint12_save_list(_SPRINT12_SCHOOLHOUSE_STUDY_SESSIONS_FILE, globals().get("_schoolhouse_study_sessions", []))
    _sprint12_save_list(_SPRINT12_SCHOOLHOUSE_WRONG_ANSWER_REVIEWS_FILE, globals().get("_schoolhouse_wrong_answer_reviews", []))
    _sprint12_save_list(_SPRINT12_SCHOOLHOUSE_WRITING_TASKS_FILE, globals().get("_schoolhouse_writing_tasks", []))
    _sprint12_save_list(_SPRINT12_CHARISMA_SELF_ASSESSMENTS_FILE, globals().get("_charisma_self_assessments", []))
    _sprint12_save_list(_SPRINT12_CHARISMA_CONVERSATION_AARS_FILE, globals().get("_charisma_conversation_aars", []))


_schoolhouse_courses = _sprint12_load_list(_SPRINT12_SCHOOLHOUSE_COURSES_FILE)
_schoolhouse_study_sessions = _sprint12_load_list(_SPRINT12_SCHOOLHOUSE_STUDY_SESSIONS_FILE)
_schoolhouse_wrong_answer_reviews = _sprint12_load_list(_SPRINT12_SCHOOLHOUSE_WRONG_ANSWER_REVIEWS_FILE)
_schoolhouse_writing_tasks = _sprint12_load_list(_SPRINT12_SCHOOLHOUSE_WRITING_TASKS_FILE)


def _schoolhouse_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _schoolhouse_find_course(course_id: str):
    for course in _schoolhouse_courses:
        if course.get("id") == course_id:
            return course
    return None


@app.get("/api/schoolhouse/status")
async def schoolhouse_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "module": "schoolhouse_learning_coach",
        "mission": "Help Kyle learn school work and durable skills without becoming dependent on AI.",
        "current_focus": [
            "WGU cybersecurity coursework",
            "OA preparation",
            "PA writing tasks",
            "Cybersecurity/GRC career alignment",
        ],
        "capabilities": [
            "course_tracker",
            "study_session_planner",
            "daily_school_brief",
            "quiz_mode",
            "wrong_answer_review",
            "writing_task_support",
            "rubric_breakdown",
            "exam_readiness",
        ],
        "courses_count": len(_schoolhouse_courses),
        "study_sessions_count": len(_schoolhouse_study_sessions),
        "teaching_rule": "Teach Kyle to understand, remember, apply, and explain the material himself.",
    }


@app.post("/api/schoolhouse/course")
async def schoolhouse_create_course(payload: Dict[str, Any]) -> Dict[str, Any]:
    course = {
        "id": str(payload.get("id") or uuid4()),
        "name": payload.get("name", "Untitled Course"),
        "code": payload.get("code", ""),
        "school": payload.get("school", "WGU"),
        "status": payload.get("status", "active"),
        "priority": payload.get("priority", "medium"),
        "competencies": payload.get("competencies", []),
        "current_task": payload.get("current_task", ""),
        "next_action": payload.get("next_action", ""),
        "created_at": _schoolhouse_now(),
        "updated_at": _schoolhouse_now(),
    }

    _schoolhouse_courses.append(course)
    _sprint12_save_capability_data()

    return {
        "status": "ok",
        "course": course,
    }


@app.get("/api/schoolhouse/courses")
async def schoolhouse_list_courses() -> Dict[str, Any]:
    return {
        "status": "ok",
        "count": len(_schoolhouse_courses),
        "courses": _schoolhouse_courses,
    }


@app.post("/api/schoolhouse/study-session")
async def schoolhouse_study_session(payload: Dict[str, Any]) -> Dict[str, Any]:
    confidence_before = int(payload.get("confidence_before", 0) or 0)
    confidence_after = int(payload.get("confidence_after", confidence_before) or confidence_before)

    session = {
        "id": str(payload.get("id") or uuid4()),
        "course": payload.get("course", ""),
        "objective": payload.get("objective", ""),
        "duration_minutes": int(payload.get("duration_minutes", 0) or 0),
        "material": payload.get("material", ""),
        "notes": payload.get("notes", ""),
        "confidence_before": confidence_before,
        "confidence_after": confidence_after,
        "blockers": payload.get("blockers", []),
        "next_action": payload.get("next_action", ""),
        "created_at": _schoolhouse_now(),
    }

    if confidence_after > confidence_before:
        readiness_signal = "improved"
    elif confidence_after == confidence_before:
        readiness_signal = "unchanged"
    else:
        readiness_signal = "declined"

    session["readiness_signal"] = readiness_signal

    _schoolhouse_study_sessions.append(session)
    _sprint12_save_capability_data()

    return {
        "status": "ok",
        "study_session": session,
    }


@app.get("/api/schoolhouse/daily-brief")
async def schoolhouse_daily_brief() -> Dict[str, Any]:
    active_courses = [
        course for course in _schoolhouse_courses
        if str(course.get("status", "")).lower() != "completed"
    ]

    high_priority_courses = [
        course for course in active_courses
        if str(course.get("priority", "")).lower() == "high"
    ]

    if high_priority_courses:
        recommended_focus = high_priority_courses[0].get("name")
        next_action = high_priority_courses[0].get("next_action") or high_priority_courses[0].get("current_task")
    elif active_courses:
        recommended_focus = active_courses[0].get("name")
        next_action = active_courses[0].get("next_action") or active_courses[0].get("current_task")
    else:
        recommended_focus = "Add your current WGU course."
        next_action = "Create a course entry and define the next study action."

    return {
        "status": "ok",
        "brief": {
            "mission": "Move school work forward today without overbuilding or context switching.",
            "recommended_focus": recommended_focus,
            "next_action": next_action,
            "active_courses": len(active_courses),
            "study_sessions_logged": len(_schoolhouse_study_sessions),
            "recommended_study_block_minutes": 45,
            "rules": [
                "Study one course at a time.",
                "Use quiz mode for recall, not passive reading.",
                "Log wrong answers immediately.",
                "End with a next action.",
            ],
        },
    }


@app.post("/api/schoolhouse/quiz")
async def schoolhouse_quiz(payload: Dict[str, Any]) -> Dict[str, Any]:
    course = payload.get("course", "")
    topic = payload.get("topic", "")
    difficulty = payload.get("difficulty", "medium")

    question = payload.get("question")
    if not question:
        question = f"Explain the most important concept from {topic or course or 'this lesson'} in your own words."

    return {
        "status": "ok",
        "mode": "one_question_at_a_time",
        "course": course,
        "topic": topic,
        "difficulty": difficulty,
        "question": question,
        "instructions": [
            "Answer without looking it up first.",
            "Use your own words.",
            "After answering, review why your answer was correct or incomplete.",
        ],
    }


@app.post("/api/schoolhouse/wrong-answer-review")
async def schoolhouse_wrong_answer_review(payload: Dict[str, Any]) -> Dict[str, Any]:
    review = {
        "id": str(payload.get("id") or uuid4()),
        "course": payload.get("course", ""),
        "question": payload.get("question", ""),
        "selected_answer": payload.get("selected_answer", ""),
        "correct_answer": payload.get("correct_answer", ""),
        "why_wrong": payload.get("why_wrong", ""),
        "rule_to_remember": payload.get("rule_to_remember", ""),
        "next_drill": payload.get("next_drill", "Create one similar question and answer it without notes."),
        "created_at": _schoolhouse_now(),
    }

    _schoolhouse_wrong_answer_reviews.append(review)
    _sprint12_save_capability_data()

    return {
        "status": "ok",
        "review": review,
        "teaching_point": "A wrong answer is useful only if it becomes a rule, example, or drill.",
    }


@app.post("/api/schoolhouse/writing-task")
async def schoolhouse_writing_task(payload: Dict[str, Any]) -> Dict[str, Any]:
    task = {
        "id": str(payload.get("id") or uuid4()),
        "course": payload.get("course", ""),
        "task_name": payload.get("task_name", ""),
        "prompt": payload.get("prompt", ""),
        "rubric_items": payload.get("rubric_items", []),
        "status": payload.get("status", "drafting"),
        "next_action": payload.get("next_action", "Break the rubric into required sections."),
        "created_at": _schoolhouse_now(),
    }

    _schoolhouse_writing_tasks.append(task)
    _sprint12_save_capability_data()

    section_plan = [
        {
            "rubric_item": item,
            "required_action": "Write a direct paragraph that satisfies this rubric item.",
        }
        for item in task["rubric_items"]
    ]

    return {
        "status": "ok",
        "writing_task": task,
        "section_plan": section_plan,
        "rule": "Answer the rubric directly. Do not write extra material that does not earn points.",
    }



# --- Sprint 09 Charisma and Communication Skill Module ---
_charisma_self_assessments = _sprint12_load_list(_SPRINT12_CHARISMA_SELF_ASSESSMENTS_FILE) if "_sprint12_load_list" in globals() else []
_charisma_conversation_aars = _sprint12_load_list(_SPRINT12_CHARISMA_CONVERSATION_AARS_FILE) if "_sprint12_load_list" in globals() else []


def _charisma_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _charisma_score(payload: Dict[str, Any]) -> Dict[str, Any]:
    fields = [
        "presence",
        "clarity",
        "listening",
        "emotional_control",
        "confidence",
        "empathy",
        "framing",
        "trust_building",
        "ethical_alignment",
    ]

    scores = {}
    for field in fields:
        try:
            value = int(payload.get(field, 0) or 0)
        except Exception:
            value = 0
        scores[field] = max(0, min(10, value))

    average = round(sum(scores.values()) / len(fields), 2)

    weakest_field = min(scores, key=scores.get)
    strongest_field = max(scores, key=scores.get)

    if average >= 8:
        level = "strong"
    elif average >= 5:
        level = "developing"
    else:
        level = "needs_foundation"

    return {
        "scores": scores,
        "average": average,
        "level": level,
        "strongest_field": strongest_field,
        "weakest_field": weakest_field,
        "recommendation": f"Focus next on {weakest_field.replace('_', ' ')}.",
    }


@app.get("/api/skills/charisma")
async def charisma_status() -> Dict[str, Any]:
    return {
        "status": "ok",
        "module": "charisma_communication_skill",
        "definition": "Charisma is ethical communication with presence, clarity, confidence, emotional intelligence, timing, and trust-building behavior.",
        "doctrine": "Charisma is not manipulation. It is ethical influence, leadership communication, active listening, emotional intelligence, and social calibration.",
        "skill_stack": [
            "presence",
            "voice",
            "listening",
            "emotional_intelligence",
            "storytelling",
            "rapport",
            "framing",
            "social_calibration",
            "leadership_communication",
            "ethical_influence",
        ],
        "use_cases": [
            "WGU instructor communication",
            "cybersecurity interviews",
            "GovCon client conversations",
            "Echo Seven sales calls",
            "family conversations",
            "leadership moments",
            "podcasting and YouTube presence",
            "networking",
        ],
        "self_assessments_count": len(_charisma_self_assessments),
        "conversation_aars_count": len(_charisma_conversation_aars),
    }


@app.post("/api/skills/charisma/self-assessment")
async def charisma_self_assessment(payload: Dict[str, Any]) -> Dict[str, Any]:
    score = _charisma_score(payload)

    assessment = {
        "id": str(payload.get("id") or uuid4()),
        "context": payload.get("context", "general"),
        "scores": score["scores"],
        "average": score["average"],
        "level": score["level"],
        "strongest_field": score["strongest_field"],
        "weakest_field": score["weakest_field"],
        "recommendation": score["recommendation"],
        "created_at": _charisma_now(),
    }

    _charisma_self_assessments.append(assessment)
    _sprint12_save_capability_data()

    return {
        "status": "ok",
        "assessment": assessment,
        "rule": "Charisma improves through repetition, feedback, and ethical self-control.",
    }


@app.get("/api/skills/charisma/daily-drill")
async def charisma_daily_drill() -> Dict[str, Any]:
    drills = [
        {
            "name": "60-second calm voice drill",
            "objective": "Practice steady pacing, lower tension, and clear tone.",
            "steps": [
                "Stand or sit upright.",
                "Breathe slowly for 10 seconds.",
                "Say your main point in one sentence.",
                "Repeat it slower with one deliberate pause.",
            ],
        },
        {
            "name": "Active listening drill",
            "objective": "Build trust by reflecting before responding.",
            "steps": [
                "Ask one clear question.",
                "Let the other person finish.",
                "Summarize what they said in one sentence.",
                "Ask if you understood correctly.",
            ],
        },
        {
            "name": "Command clarity drill",
            "objective": "Communicate direction without rambling.",
            "steps": [
                "State the outcome.",
                "State the reason.",
                "State the next action.",
                "Stop talking.",
            ],
        },
        {
            "name": "Reframe drill",
            "objective": "Turn a tense conversation into a solvable problem.",
            "steps": [
                "Name the issue without blame.",
                "State the shared objective.",
                "Offer one next step.",
                "Ask for confirmation.",
            ],
        },
    ]

    day_index = datetime.now(timezone.utc).timetuple().tm_yday % len(drills)
    drill = drills[day_index]

    return {
        "status": "ok",
        "drill": drill,
        "duration_minutes": 5,
        "instruction": "Do the drill once today before an important conversation.",
    }


@app.post("/api/skills/charisma/conversation-aar")
async def charisma_conversation_aar(payload: Dict[str, Any]) -> Dict[str, Any]:
    score_payload = payload.get("scorecard", {})
    score = _charisma_score(score_payload)

    aar = {
        "id": str(payload.get("id") or uuid4()),
        "objective": payload.get("objective", ""),
        "audience": payload.get("audience", ""),
        "what_i_said": payload.get("what_i_said", ""),
        "how_they_responded": payload.get("how_they_responded", ""),
        "did_i_listen_well": payload.get("did_i_listen_well", ""),
        "did_i_stay_calm": payload.get("did_i_stay_calm", ""),
        "did_i_build_trust": payload.get("did_i_build_trust", ""),
        "what_to_improve": payload.get("what_to_improve", ""),
        "score": score,
        "created_at": _charisma_now(),
    }

    if not aar["what_to_improve"]:
        aar["what_to_improve"] = score["recommendation"]

    _charisma_conversation_aars.append(aar)
    _sprint12_save_capability_data()

    return {
        "status": "ok",
        "conversation_aar": aar,
        "teaching_point": "The goal is not to win every conversation. The goal is to communicate clearly, listen accurately, and build trust ethically.",
    }



# --- Sprint 10 Command Dashboard Integration ---
from fastapi.responses import HTMLResponse as _Sprint10HTMLResponse


def _sprint10_safe_len(name: str) -> int:
    value = globals().get(name, [])
    try:
        return len(value)
    except Exception:
        return 0


def _sprint10_integrated_missions_summary() -> Dict[str, Any]:
    try:
        return _sprint07_mission_summary()
    except Exception:
        missions = list(globals().get("_sprint01_missions", {}).values())
        return {
            "total": len(missions),
            "active": len(missions),
            "completed": 0,
            "blocked": 0,
        }


def _sprint10_latest_daily_brief() -> Dict[str, Any]:
    try:
        return _sprint07_latest_brief()
    except Exception:
        return {
            "commander_intent": "Run Project Salus daily.",
            "top_priorities": [],
            "risks": [],
            "next_actions": [],
        }


@app.get("/api/command/integrated-state")
async def sprint10_integrated_command_state() -> Dict[str, Any]:
    return {
        "status": "ok",
        "module": "command_dashboard_integration",
        "dashboard": "integrated_command",
        "daily_use": {
            "mode": "real_daily_use",
            "daily_brief": _sprint10_latest_daily_brief(),
            "missions_summary": _sprint10_integrated_missions_summary(),
            "aar_count": _sprint07_aar_count() if "_sprint07_aar_count" in globals() else 0,
        },
        "schoolhouse": {
            "module": "schoolhouse_learning_coach",
            "courses_count": _sprint10_safe_len("_schoolhouse_courses"),
            "study_sessions_count": _sprint10_safe_len("_schoolhouse_study_sessions"),
            "wrong_answer_reviews_count": _sprint10_safe_len("_schoolhouse_wrong_answer_reviews"),
            "writing_tasks_count": _sprint10_safe_len("_schoolhouse_writing_tasks"),
            "primary_focus": "WGU cybersecurity coursework",
        },
        "charisma": {
            "module": "charisma_communication_skill",
            "self_assessments_count": _sprint10_safe_len("_charisma_self_assessments"),
            "conversation_aars_count": _sprint10_safe_len("_charisma_conversation_aars"),
            "primary_focus": "Ethical communication, presence, listening, and trust-building",
        },
        "next_actions": [
            "Review daily-use mission status.",
            "Open Schoolhouse daily brief.",
            "Run one charisma drill.",
            "Close the day with an AAR.",
        ],
    }


@app.get("/command/integrated", response_class=_Sprint10HTMLResponse)
async def sprint10_integrated_command_dashboard() -> _Sprint10HTMLResponse:
    html = """
    <!doctype html>
    <html>
      <head>
        <title>Project Salus — Integrated Command Dashboard</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            background: #07111f;
            color: #f4f7fb;
            margin: 0;
            padding: 32px;
          }
          h1, h2 {
            color: #d7b46a;
          }
          .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 18px;
          }
          .panel {
            border: 1px solid #28405f;
            border-radius: 12px;
            padding: 20px;
            background: #0d1c2f;
          }
          button, a.button {
            display: inline-block;
            background: #d7b46a;
            color: #07111f;
            border: none;
            padding: 10px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            margin: 4px 4px 4px 0;
          }
          pre {
            white-space: pre-wrap;
            background: #081525;
            padding: 14px;
            border-radius: 8px;
            border: 1px solid #28405f;
            max-height: 320px;
            overflow: auto;
          }
          .muted {
            color: #aab7c7;
          }
        </style>
      </head>
      <body>
        <h1>Project Salus — Integrated Command Dashboard</h1>
        <p class="muted">Daily Use + Schoolhouse + Charisma</p>

        <div class="panel">
          <h2>Command State</h2>
          <button onclick="refreshIntegratedState()">Refresh Integrated State</button>
          <a class="button" href="/command/daily">Open Daily Use Mode</a>
          <pre id="integratedState">Loading...</pre>
        </div>

        <div class="grid">
          <div class="panel">
            <h2>Daily Use</h2>
            <p>Mission tracker, daily brief, and AAR loop.</p>
            <button onclick="loadDailyUse()">Load Daily Use State</button>
            <pre id="dailyUse">Ready.</pre>
          </div>

          <div class="panel">
            <h2>Schoolhouse</h2>
            <p>WGU learning coach, study brief, quiz mode, and wrong-answer review.</p>
            <button onclick="loadSchoolhouseBrief()">Load Schoolhouse Brief</button>
            <pre id="schoolhouse">Ready.</pre>
          </div>

          <div class="panel">
            <h2>Charisma</h2>
            <p>Presence, listening, ethical influence, and communication drills.</p>
            <button onclick="loadCharismaDrill()">Load Charisma Drill</button>
            <pre id="charisma">Ready.</pre>
          </div>
        </div>

        <script>
          async function getJson(path) {
            const res = await fetch(path);
            return await res.json();
          }

          function show(id, data) {
            document.getElementById(id).textContent = JSON.stringify(data, null, 2);
          }

          async function refreshIntegratedState() {
            show("integratedState", await getJson("/api/command/integrated-state"));
          }

          async function loadDailyUse() {
            show("dailyUse", await getJson("/api/daily-use/state"));
          }

          async function loadSchoolhouseBrief() {
            show("schoolhouse", await getJson("/api/schoolhouse/daily-brief"));
          }

          async function loadCharismaDrill() {
            show("charisma", await getJson("/api/skills/charisma/daily-drill"));
          }

          refreshIntegratedState();
        </script>
      </body>
    </html>
    """
    return _Sprint10HTMLResponse(content=html)



# --- Sprint 11 Operational Dashboard Controls ---
from fastapi.responses import HTMLResponse as _Sprint11HTMLResponse


@app.get("/command/ops", response_class=_Sprint11HTMLResponse)
async def sprint11_operational_dashboard() -> _Sprint11HTMLResponse:
    html = """
    <!doctype html>
    <html>
      <head>
        <title>Project Salus — Operational Dashboard</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            background: #07111f;
            color: #f4f7fb;
            margin: 0;
            padding: 32px;
          }
          h1, h2 {
            color: #d7b46a;
          }
          .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 18px;
          }
          .panel {
            border: 1px solid #28405f;
            border-radius: 12px;
            padding: 20px;
            background: #0d1c2f;
            margin-bottom: 18px;
          }
          input, textarea, select {
            width: 100%;
            box-sizing: border-box;
            margin: 6px 0 12px 0;
            padding: 10px;
            border-radius: 8px;
            border: 1px solid #28405f;
            background: #081525;
            color: #f4f7fb;
          }
          button, a.button {
            display: inline-block;
            background: #d7b46a;
            color: #07111f;
            border: none;
            padding: 10px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            margin: 4px 4px 4px 0;
          }
          pre {
            white-space: pre-wrap;
            background: #081525;
            padding: 14px;
            border-radius: 8px;
            border: 1px solid #28405f;
            max-height: 360px;
            overflow: auto;
          }
          .muted {
            color: #aab7c7;
          }
        </style>
      </head>
      <body>
        <h1>Project Salus — Operational Dashboard</h1>
        <p class="muted">Daily command controls for missions, school, and communication training.</p>

        <div class="panel">
          <h2>Integrated Command State</h2>
          <button onclick="refreshState()">Refresh State</button>
          <a class="button" href="/command/integrated">View Integrated Dashboard</a>
          <a class="button" href="/command/daily">View Daily Mode</a>
          <pre id="state">Ready.</pre>
        </div>

        <div class="grid">
          <div class="panel">
            <h2>Daily Brief</h2>
            <input id="brief_intent" placeholder="Commander intent" value="Execute today's highest-leverage missions.">
            <textarea id="brief_priorities" placeholder="Top priorities, one per line"></textarea>
            <textarea id="brief_risks" placeholder="Risks, one per line"></textarea>
            <textarea id="brief_actions" placeholder="Next actions, one per line"></textarea>
            <button onclick="createDailyBrief()">Create Daily Brief</button>
          </div>

          <div class="panel">
            <h2>Mission</h2>
            <input id="mission_title" placeholder="Mission title">
            <textarea id="mission_intent" placeholder="Mission intent"></textarea>
            <select id="mission_priority">
              <option>high</option>
              <option>medium</option>
              <option>low</option>
            </select>
            <select id="mission_status">
              <option>planned</option>
              <option>in_progress</option>
              <option>blocked</option>
              <option>completed</option>
            </select>
            <input id="mission_next_action" placeholder="Next action">
            <button onclick="createMission()">Create Mission</button>
          </div>

          <div class="panel">
            <h2>Schoolhouse Course</h2>
            <input id="course_name" placeholder="Course name" value="Practical Applications of Prompt">
            <input id="course_code" placeholder="Course code" value="Prompt-OA">
            <select id="course_priority">
              <option>high</option>
              <option>medium</option>
              <option>low</option>
            </select>
            <input id="course_task" placeholder="Current task" value="OA retake preparation">
            <input id="course_next" placeholder="Next action" value="Run one-question quiz drills">
            <button onclick="createCourse()">Add Course</button>
          </div>

          <div class="panel">
            <h2>Schoolhouse Study Session</h2>
            <input id="study_course" placeholder="Course" value="Practical Applications of Prompt">
            <input id="study_objective" placeholder="Objective">
            <input id="study_minutes" placeholder="Duration minutes" value="45">
            <textarea id="study_notes" placeholder="Notes"></textarea>
            <input id="study_confidence_before" placeholder="Confidence before 0-10" value="4">
            <input id="study_confidence_after" placeholder="Confidence after 0-10" value="6">
            <input id="study_next" placeholder="Next action">
            <button onclick="logStudySession()">Log Study Session</button>
          </div>

          <div class="panel">
            <h2>Charisma Self-Assessment</h2>
            <input id="charisma_context" placeholder="Context" value="General communication">
            <input id="presence" placeholder="Presence 0-10" value="7">
            <input id="clarity" placeholder="Clarity 0-10" value="7">
            <input id="listening" placeholder="Listening 0-10" value="6">
            <input id="emotional_control" placeholder="Emotional control 0-10" value="7">
            <input id="confidence" placeholder="Confidence 0-10" value="7">
            <input id="empathy" placeholder="Empathy 0-10" value="6">
            <input id="framing" placeholder="Framing 0-10" value="6">
            <input id="trust_building" placeholder="Trust building 0-10" value="6">
            <input id="ethical_alignment" placeholder="Ethical alignment 0-10" value="10">
            <button onclick="createCharismaAssessment()">Save Self-Assessment</button>
          </div>

          <div class="panel">
            <h2>Charisma Conversation AAR</h2>
            <input id="aar_objective" placeholder="Conversation objective">
            <input id="aar_audience" placeholder="Audience">
            <textarea id="aar_said" placeholder="What I said"></textarea>
            <textarea id="aar_response" placeholder="How they responded"></textarea>
            <input id="aar_listen" placeholder="Did I listen well?">
            <input id="aar_calm" placeholder="Did I stay calm?">
            <input id="aar_trust" placeholder="Did I build trust?">
            <input id="aar_improve" placeholder="What to improve next time">
            <button onclick="logConversationAAR()">Log Conversation AAR</button>
          </div>
        </div>

        <div class="panel">
          <h2>Last Action Result</h2>
          <pre id="result">No action yet.</pre>
        </div>

        <script>
          async function api(path, options = {}) {
            const res = await fetch(path, {
              headers: { "Content-Type": "application/json" },
              ...options
            });
            return await res.json();
          }

          function value(id) {
            return document.getElementById(id).value;
          }

          function intValue(id) {
            const parsed = parseInt(value(id), 10);
            return Number.isNaN(parsed) ? 0 : parsed;
          }

          function lines(id) {
            return value(id).split("\\n").map(x => x.trim()).filter(Boolean);
          }

          function show(id, data) {
            document.getElementById(id).textContent = JSON.stringify(data, null, 2);
          }

          async function refreshState() {
            show("state", await api("/api/command/integrated-state"));
          }

          async function afterAction(data) {
            show("result", data);
            await refreshState();
          }

          async function createDailyBrief() {
            await afterAction(await api("/api/daily-use/brief", {
              method: "POST",
              body: JSON.stringify({
                commander_intent: value("brief_intent"),
                top_priorities: lines("brief_priorities"),
                risks: lines("brief_risks"),
                next_actions: lines("brief_actions")
              })
            }));
          }

          async function createMission() {
            await afterAction(await api("/missions", {
              method: "POST",
              body: JSON.stringify({
                title: value("mission_title"),
                intent: value("mission_intent"),
                priority: value("mission_priority"),
                status: value("mission_status"),
                risk: "not_assessed",
                next_action: value("mission_next_action")
              })
            }));
          }

          async function createCourse() {
            await afterAction(await api("/api/schoolhouse/course", {
              method: "POST",
              body: JSON.stringify({
                name: value("course_name"),
                code: value("course_code"),
                school: "WGU",
                priority: value("course_priority"),
                current_task: value("course_task"),
                next_action: value("course_next")
              })
            }));
          }

          async function logStudySession() {
            await afterAction(await api("/api/schoolhouse/study-session", {
              method: "POST",
              body: JSON.stringify({
                course: value("study_course"),
                objective: value("study_objective"),
                duration_minutes: intValue("study_minutes"),
                notes: value("study_notes"),
                confidence_before: intValue("study_confidence_before"),
                confidence_after: intValue("study_confidence_after"),
                next_action: value("study_next"),
                blockers: []
              })
            }));
          }

          function charismaScorecard() {
            return {
              presence: intValue("presence"),
              clarity: intValue("clarity"),
              listening: intValue("listening"),
              emotional_control: intValue("emotional_control"),
              confidence: intValue("confidence"),
              empathy: intValue("empathy"),
              framing: intValue("framing"),
              trust_building: intValue("trust_building"),
              ethical_alignment: intValue("ethical_alignment")
            };
          }

          async function createCharismaAssessment() {
            await afterAction(await api("/api/skills/charisma/self-assessment", {
              method: "POST",
              body: JSON.stringify({
                context: value("charisma_context"),
                ...charismaScorecard()
              })
            }));
          }

          async function logConversationAAR() {
            await afterAction(await api("/api/skills/charisma/conversation-aar", {
              method: "POST",
              body: JSON.stringify({
                objective: value("aar_objective"),
                audience: value("aar_audience"),
                what_i_said: value("aar_said"),
                how_they_responded: value("aar_response"),
                did_i_listen_well: value("aar_listen"),
                did_i_stay_calm: value("aar_calm"),
                did_i_build_trust: value("aar_trust"),
                what_to_improve: value("aar_improve"),
                scorecard: charismaScorecard()
              })
            }));
          }

          refreshState();
        </script>
      </body>
    </html>
    """
    return _Sprint11HTMLResponse(content=html)



# --- Sprint 13 Operational Review and History Dashboard ---
from fastapi.responses import HTMLResponse as _Sprint13HTMLResponse


def _sprint13_safe_list(name: str) -> list:
    value = globals().get(name, [])
    if isinstance(value, dict):
        return list(value.values())
    if isinstance(value, list):
        return value
    return []


def _sprint13_review_count(data: list) -> int:
    try:
        return len(data)
    except Exception:
        return 0


@app.get("/api/command/review-state")
async def sprint13_review_state() -> Dict[str, Any]:
    daily_briefs = _sprint13_safe_list("_sprint01_daily_briefs")
    missions = _sprint13_safe_list("_sprint01_missions")
    aars = _sprint13_safe_list("_sprint04_aars")

    schoolhouse_courses = _sprint13_safe_list("_schoolhouse_courses")
    schoolhouse_study_sessions = _sprint13_safe_list("_schoolhouse_study_sessions")
    schoolhouse_wrong_answer_reviews = _sprint13_safe_list("_schoolhouse_wrong_answer_reviews")
    schoolhouse_writing_tasks = _sprint13_safe_list("_schoolhouse_writing_tasks")

    charisma_self_assessments = _sprint13_safe_list("_charisma_self_assessments")
    charisma_conversation_aars = _sprint13_safe_list("_charisma_conversation_aars")

    return {
        "status": "ok",
        "module": "operational_review_history",
        "review_sections": [
            "daily_briefs",
            "missions",
            "aars",
            "schoolhouse_courses",
            "schoolhouse_study_sessions",
            "schoolhouse_wrong_answer_reviews",
            "schoolhouse_writing_tasks",
            "charisma_self_assessments",
            "charisma_conversation_aars",
        ],
        "counts": {
            "daily_briefs": _sprint13_review_count(daily_briefs),
            "missions": _sprint13_review_count(missions),
            "aars": _sprint13_review_count(aars),
            "schoolhouse_courses": _sprint13_review_count(schoolhouse_courses),
            "schoolhouse_study_sessions": _sprint13_review_count(schoolhouse_study_sessions),
            "schoolhouse_wrong_answer_reviews": _sprint13_review_count(schoolhouse_wrong_answer_reviews),
            "schoolhouse_writing_tasks": _sprint13_review_count(schoolhouse_writing_tasks),
            "charisma_self_assessments": _sprint13_review_count(charisma_self_assessments),
            "charisma_conversation_aars": _sprint13_review_count(charisma_conversation_aars),
        },
        "data": {
            "daily_briefs": daily_briefs,
            "missions": missions,
            "aars": aars,
            "schoolhouse_courses": schoolhouse_courses,
            "schoolhouse_study_sessions": schoolhouse_study_sessions,
            "schoolhouse_wrong_answer_reviews": schoolhouse_wrong_answer_reviews,
            "schoolhouse_writing_tasks": schoolhouse_writing_tasks,
            "charisma_self_assessments": charisma_self_assessments,
            "charisma_conversation_aars": charisma_conversation_aars,
        },
        "next_action": "Review stored data and identify what should be edited, deleted, or promoted into the daily brief.",
    }


@app.get("/command/review", response_class=_Sprint13HTMLResponse)
async def sprint13_review_dashboard() -> _Sprint13HTMLResponse:
    html = """
    <!doctype html>
    <html>
      <head>
        <title>Project Salus — Review Dashboard</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            background: #07111f;
            color: #f4f7fb;
            margin: 0;
            padding: 32px;
          }
          h1, h2 {
            color: #d7b46a;
          }
          .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(360px, 1fr));
            gap: 18px;
          }
          .panel {
            border: 1px solid #28405f;
            border-radius: 12px;
            padding: 20px;
            background: #0d1c2f;
            margin-bottom: 18px;
          }
          button, a.button {
            display: inline-block;
            background: #d7b46a;
            color: #07111f;
            border: none;
            padding: 10px 14px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            margin: 4px 4px 4px 0;
          }
          pre {
            white-space: pre-wrap;
            background: #081525;
            padding: 14px;
            border-radius: 8px;
            border: 1px solid #28405f;
            max-height: 420px;
            overflow: auto;
          }
          .muted {
            color: #aab7c7;
          }
        </style>
      </head>
      <body>
        <h1>Project Salus — Operational Review Dashboard</h1>
        <p class="muted">Review stored missions, school data, charisma data, and AAR history.</p>

        <div class="panel">
          <h2>Review Controls</h2>
          <button onclick="refreshReview()">Refresh Review State</button>
          <a class="button" href="/command/ops">Open Operational Dashboard</a>
          <a class="button" href="/command/integrated">Open Integrated Dashboard</a>
          <pre id="counts">Loading...</pre>
        </div>

        <div class="grid">
          <div class="panel">
            <h2>Daily Briefs</h2>
            <pre id="daily_briefs">Loading...</pre>
          </div>

          <div class="panel">
            <h2>Missions</h2>
            <pre id="missions">Loading...</pre>
          </div>

          <div class="panel">
            <h2>AAR History</h2>
            <pre id="aars">Loading...</pre>
          </div>

          <div class="panel">
            <h2>Schoolhouse Courses</h2>
            <pre id="schoolhouse_courses">Loading...</pre>
          </div>

          <div class="panel">
            <h2>Schoolhouse Study Sessions</h2>
            <pre id="schoolhouse_study_sessions">Loading...</pre>
          </div>

          <div class="panel">
            <h2>Schoolhouse Wrong-Answer Reviews</h2>
            <pre id="schoolhouse_wrong_answer_reviews">Loading...</pre>
          </div>

          <div class="panel">
            <h2>Schoolhouse Writing Tasks</h2>
            <pre id="schoolhouse_writing_tasks">Loading...</pre>
          </div>

          <div class="panel">
            <h2>Charisma Self-Assessments</h2>
            <pre id="charisma_self_assessments">Loading...</pre>
          </div>

          <div class="panel">
            <h2>Charisma Conversation AARs</h2>
            <pre id="charisma_conversation_aars">Loading...</pre>
          </div>
        </div>

        <script>
          async function getJson(path) {
            const res = await fetch(path);
            return await res.json();
          }

          function show(id, data) {
            document.getElementById(id).textContent = JSON.stringify(data, null, 2);
          }

          async function refreshReview() {
            const state = await getJson("/api/command/review-state");
            show("counts", state.counts);
            show("daily_briefs", state.data.daily_briefs);
            show("missions", state.data.missions);
            show("aars", state.data.aars);
            show("schoolhouse_courses", state.data.schoolhouse_courses);
            show("schoolhouse_study_sessions", state.data.schoolhouse_study_sessions);
            show("schoolhouse_wrong_answer_reviews", state.data.schoolhouse_wrong_answer_reviews);
            show("schoolhouse_writing_tasks", state.data.schoolhouse_writing_tasks);
            show("charisma_self_assessments", state.data.charisma_self_assessments);
            show("charisma_conversation_aars", state.data.charisma_conversation_aars);
          }

          refreshReview();
        </script>
      </body>
    </html>
    """
    return _Sprint13HTMLResponse(content=html)



# --- Sprint 14 Command Launcher and Navigation System ---
from fastapi.responses import HTMLResponse as _Sprint14HTMLResponse


def _sprint14_count(name: str) -> int:
    value = globals().get(name, [])
    if isinstance(value, dict):
        return len(value)
    if isinstance(value, list):
        return len(value)
    return 0


@app.get("/api/command/health")
async def sprint14_command_health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "module": "command_launcher_navigation",
        "system": "Project Salus Mission Control",
        "primary_pages": {
            "home": "/",
            "launcher": "/command/home",
            "ops_dashboard": "/command/ops",
            "review_dashboard": "/command/review",
            "integrated_dashboard": "/command/integrated",
            "daily_mode": "/command/daily",
        },
        "api_endpoints": {
            "health": "/api/command/health",
            "integrated_state": "/api/command/integrated-state",
            "review_state": "/api/command/review-state",
            "daily_use_state": "/api/daily-use/state",
            "schoolhouse_status": "/api/schoolhouse/status",
            "charisma_status": "/api/skills/charisma",
        },
        "data_counts": {
            "missions": _sprint14_count("_sprint01_missions"),
            "daily_briefs": _sprint14_count("_sprint01_daily_briefs"),
            "aars": _sprint14_count("_sprint04_aars"),
            "schoolhouse_courses": _sprint14_count("_schoolhouse_courses"),
            "schoolhouse_study_sessions": _sprint14_count("_schoolhouse_study_sessions"),
            "charisma_self_assessments": _sprint14_count("_charisma_self_assessments"),
            "charisma_conversation_aars": _sprint14_count("_charisma_conversation_aars"),
        },
        "next_action": "Open /command/ops for daily work or /command/review to inspect saved data.",
    }


def _sprint14_launcher_html(title: str) -> str:
    return f"""
    <!doctype html>
    <html>
      <head>
        <title>{title}</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            background: #07111f;
            color: #f4f7fb;
            margin: 0;
            padding: 32px;
          }}
          h1, h2 {{
            color: #d7b46a;
          }}
          .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 18px;
          }}
          .panel {{
            border: 1px solid #28405f;
            border-radius: 12px;
            padding: 20px;
            background: #0d1c2f;
            margin-bottom: 18px;
          }}
          a.button, button {{
            display: inline-block;
            background: #d7b46a;
            color: #07111f;
            border: none;
            padding: 11px 15px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            margin: 5px 5px 5px 0;
          }}
          pre {{
            white-space: pre-wrap;
            background: #081525;
            padding: 14px;
            border-radius: 8px;
            border: 1px solid #28405f;
            max-height: 360px;
            overflow: auto;
          }}
          .muted {{
            color: #aab7c7;
          }}
        </style>
      </head>
      <body>
        <h1>Project Salus Mission Control</h1>
        <p class="muted">Command launcher for Kyle's daily operating system.</p>

        <div class="panel">
          <h2>Primary Actions</h2>
          <a class="button" href="/command/ops">Open Operational Dashboard</a>
          <a class="button" href="/command/review">Open Review Dashboard</a>
          <a class="button" href="/command/integrated">Open Integrated Dashboard</a>
          <a class="button" href="/command/daily">Open Daily Mode</a>
          <button onclick="loadHealth()">Check Health</button>
          <pre id="health">Click Check Health.</pre>
        </div>

        <div class="grid">
          <div class="panel">
            <h2>Daily Operations</h2>
            <p>Create daily briefs, missions, study sessions, and communication AARs.</p>
            <a class="button" href="/command/ops">Go to Ops</a>
          </div>

          <div class="panel">
            <h2>Review History</h2>
            <p>Review stored missions, Schoolhouse data, Charisma records, and AAR history.</p>
            <a class="button" href="/command/review">Go to Review</a>
          </div>

          <div class="panel">
            <h2>Schoolhouse</h2>
            <p>Learning coach for WGU, cybersecurity, AI, and durable skill development.</p>
            <a class="button" href="/api/schoolhouse/status">Schoolhouse Status</a>
            <a class="button" href="/api/schoolhouse/daily-brief">School Brief</a>
          </div>

          <div class="panel">
            <h2>Charisma</h2>
            <p>Presence, listening, communication clarity, and ethical influence training.</p>
            <a class="button" href="/api/skills/charisma">Charisma Status</a>
            <a class="button" href="/api/skills/charisma/daily-drill">Daily Drill</a>
          </div>
        </div>

        <script>
          async function loadHealth() {{
            const res = await fetch("/api/command/health");
            const data = await res.json();
            document.getElementById("health").textContent = JSON.stringify(data, null, 2);
          }}
        </script>
      </body>
    </html>
    """


@app.get("/", response_class=_Sprint14HTMLResponse)
async def sprint14_home_page() -> _Sprint14HTMLResponse:
    return _Sprint14HTMLResponse(content=_sprint14_launcher_html("Project Salus Mission Control"))


@app.get("/command/home", response_class=_Sprint14HTMLResponse)
async def sprint14_command_home_page() -> _Sprint14HTMLResponse:
    return _Sprint14HTMLResponse(content=_sprint14_launcher_html("Project Salus — Command Home"))

# --- Sprint 23 Wire Extracted Dashboard and Readiness Routers ---
from backend.routes.dashboard_index import router as _sprint23_dashboard_index_router
from backend.routes.readiness import router as _sprint23_readiness_router

app.include_router(_sprint23_dashboard_index_router)
app.include_router(_sprint23_readiness_router)


# --- Sprint 24 Extract Navigation and Workflow Routers ---
from backend.routes.navigation import router as _sprint24_navigation_router
from backend.routes.workflows import router as _sprint24_workflows_router

app.include_router(_sprint24_navigation_router)
app.include_router(_sprint24_workflows_router)


# --- Sprint 26 Wire Records and Daily Driver Routers ---
from backend.routes.records import router as _sprint26_records_router
from backend.routes.daily_driver import router as _sprint26_daily_driver_router

app.include_router(_sprint26_records_router)
app.include_router(_sprint26_daily_driver_router)


# --- Phase II Epic 1 Knowledge Engine Router ---
from backend.routes.knowledge import router as _phase2_knowledge_router

app.include_router(_phase2_knowledge_router)


# --- Phase II Epic 2 Memory Engine Router ---
from backend.routes.salus_memory import router as _phase2_memory_router

app.include_router(_phase2_memory_router)


# --- Phase II Epic 3 Judgment Engine Router ---
from backend.routes.judgment_engine import router as _phase2_judgment_engine_router

app.include_router(_phase2_judgment_engine_router)


# --- Phase II Core Identity Router ---
from backend.routes.core_identity import router as _phase2_core_identity_router

app.include_router(_phase2_core_identity_router)


# --- Salus Kernel v0.1 Router ---
from backend.routes.kernel import router as _salus_kernel_router

app.include_router(_salus_kernel_router)


# --- Phase III Teaching Engine Router ---
from backend.routes.teaching_engine import router as _phase_iii_teaching_engine_router

app.include_router(_phase_iii_teaching_engine_router)


# --- Master Sprint Core OS Router ---
from backend.routes.core_os import router as _master_core_os_router

app.include_router(_master_core_os_router)


from backend.routes import decision_firewall as _decision_firewall_router
app.include_router(_decision_firewall_router.router)


from backend.routes import ai_governance as _ai_governance_router
app.include_router(_ai_governance_router.router)


from backend.routes import wealth_os as _wealth_os_router
app.include_router(_wealth_os_router.router)


from backend.routes import echo_seven_assessment as _echo_seven_assessment_router
app.include_router(_echo_seven_assessment_router.router)


from backend.routes import daily_brief as _daily_brief_v2_router
app.include_router(_daily_brief_v2_router.router)


from backend.routes import strategy_critical_thinking as _strategy_critical_thinking_router
app.include_router(_strategy_critical_thinking_router.router)


from backend.routes import mission_execution as _mission_execution_router
app.include_router(_mission_execution_router.router)


from backend.routes import mission_registry as _mission_registry_router
app.include_router(_mission_registry_router.router)


from backend.routes import command_center as _command_center_router
app.include_router(_command_center_router.router)


from backend.routes import doctrine_registry as _doctrine_registry_router
app.include_router(_doctrine_registry_router.router)


from backend.routes import intelligence_intake as _intelligence_intake_router
app.include_router(_intelligence_intake_router.router)


from backend.routes import curiosity_parking_lot as _curiosity_parking_lot_router
app.include_router(_curiosity_parking_lot_router.router)


from backend.routes import workflow_orchestrator as _workflow_orchestrator_router
app.include_router(_workflow_orchestrator_router.router)


from backend.routes import build_accelerator as _build_accelerator_router
app.include_router(_build_accelerator_router.router)

from backend.routes import mission_control_model_provider_api as _mission_control_model_provider_api_router
from backend.routes import mission_control_tool_adapter_api as _mission_control_tool_adapter_api_router
from backend.routes import mission_control_firewall_api as _mission_control_firewall_api_router
from backend.routes import mission_control_agent_runtime_api as _mission_control_agent_runtime_api_router
from backend.routes import mission_control_connector_api as _mission_control_connector_api_router
from backend.routes import mission_control_mvp_api as _mission_control_mvp_api_router
from backend.routes import mission_control_snapshot_api as _mission_control_snapshot_api_router
from backend.routes import mission_control_health_api as _mission_control_health_api_router
from backend.routes import mission_control_agent_api as _mission_control_agent_api_router
from backend.routes import mission_control_external_api as _mission_control_external_api_router
from backend.routes import mission_control_ui as _mission_control_ui_router
app.include_router(_mission_control_model_provider_api_router.router)
app.include_router(_mission_control_tool_adapter_api_router.router)
app.include_router(_mission_control_firewall_api_router.router)
app.include_router(_mission_control_agent_runtime_api_router.router)
app.include_router(_mission_control_connector_api_router.router)
app.include_router(_mission_control_mvp_api_router.router)
app.include_router(_mission_control_snapshot_api_router.router)
app.include_router(_mission_control_health_api_router.router)
app.include_router(_mission_control_agent_api_router.router)
app.include_router(_mission_control_external_api_router.router)
app.include_router(_mission_control_ui_router.router)

from backend.routes import command_home as _command_home_router
app.include_router(_command_home_router.router)
