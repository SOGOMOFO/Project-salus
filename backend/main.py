from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

from backend.database import init_db, seed_data, get_connection
from backend.api.memory import router as memory_router
from backend.memory.registry import discover_agents
from backend.memory.service import MemoryEngine
from backend.memory.memory_engine import initialize_memory_store

SALUS_PASSPHRASE = os.getenv("SALUS_PASSPHRASE", "salus-secure")
memory_engine = MemoryEngine()
memory_engine.initialize()
initialize_memory_store()


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


def verify_passphrase(x_salus_passphrase: str | None):
    if x_salus_passphrase != SALUS_PASSPHRASE:
        raise HTTPException(status_code=401, detail="Unauthorized access denied")


@app.get("/", response_class=HTMLResponse)
async def home():
    return TEMPLATE_PATH.read_text()


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "0.4.0"}


@app.get("/plugins/health")
async def plugin_health():
    plugins = []
    for agent in discover_agents():
        plugins.append({
            "name": agent["name"],
            "status": agent["status"],
            "module": agent["module"],
        })
    return {"plugins": plugins, "count": len(plugins)}


@app.get("/system/status")
async def system_status():
    agents = discover_agents()
    memory_snapshot = memory_engine.list()[:5]
    return {
        "status": "ok",
        "version": "0.4.0",
        "components": {
            "memory": {"status": "ready", "entries": len(memory_snapshot)},
            "agent_registry": {"status": "ready", "count": len(agents)},
            "api": {"status": "ready"},
        },
        "plugins": [
            {"name": agent["name"], "status": agent["status"]} for agent in agents
        ],
    }


@app.get("/core/status")
async def core_status():
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


@app.get("/core/agents")
async def core_agents(x_salus_passphrase: str | None = Header(default=None)):
    verify_passphrase(x_salus_passphrase)
    agents = discover_agents()
    return {"status": "ok", "agents": agents}


@app.get("/core/plugins/status")
async def core_plugins_status(x_salus_passphrase: str | None = Header(default=None)):
    verify_passphrase(x_salus_passphrase)
    return await plugin_health()


@app.post("/auth")
async def auth(request: Request):
    data = await request.json()
    passphrase = data.get("passphrase", "")

    if passphrase == SALUS_PASSPHRASE:
        return {
            "status": "authorized",
            "message": "Access granted to Project Salus Mission Control"
        }

    raise HTTPException(status_code=401, detail="Invalid passphrase")


@app.get("/missions")
async def missions(x_salus_passphrase: str | None = Header(default=None)):
    verify_passphrase(x_salus_passphrase)

    conn = get_connection()
    rows = conn.execute("SELECT * FROM missions ORDER BY id").fetchall()
    conn.close()
    return {"missions": [dict(row) for row in rows]}


@app.get("/agents")
async def agents(x_salus_passphrase: str | None = Header(default=None)):
    verify_passphrase(x_salus_passphrase)

    conn = get_connection()
    rows = conn.execute("SELECT * FROM agents ORDER BY id").fetchall()
    conn.close()
    return {"agents": [dict(row) for row in rows]}


@app.get("/sitreps")
async def sitreps(x_salus_passphrase: str | None = Header(default=None)):
    verify_passphrase(x_salus_passphrase)

    conn = get_connection()
    rows = conn.execute("SELECT * FROM sitreps ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    return {"sitreps": [dict(row) for row in rows]}


@app.post("/sitreps")
async def create_sitrep(
    request: Request,
    x_salus_passphrase: str | None = Header(default=None)
):
    verify_passphrase(x_salus_passphrase)

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