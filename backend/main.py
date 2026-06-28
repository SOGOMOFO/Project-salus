from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.database import init_db, seed_data, get_connection

app = FastAPI(
    title="Project Salus",
    version="0.3.0",
    description="Mission Control Backend"
)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = BASE_DIR / "frontend" / "templates" / "index.html"
STATIC_DIR = BASE_DIR / "frontend" / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.on_event("startup")
async def startup():
    init_db()
    seed_data()

@app.get("/", response_class=HTMLResponse)
async def home():
    return TEMPLATE_PATH.read_text()

@app.get("/health")
async def health():
    return {"status": "healthy", "version": "0.3.0"}

@app.get("/missions")
async def missions():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM missions ORDER BY id").fetchall()
    conn.close()
    return {"missions": [dict(row) for row in rows]}

@app.get("/agents")
async def agents():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM agents ORDER BY id").fetchall()
    conn.close()
    return {"agents": [dict(row) for row in rows]}

@app.get("/sitreps")
async def sitreps():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM sitreps ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    return {"sitreps": [dict(row) for row in rows]}

@app.post("/sitreps")
async def create_sitrep(request: Request):
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
