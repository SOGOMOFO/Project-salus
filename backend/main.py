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
