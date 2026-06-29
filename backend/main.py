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