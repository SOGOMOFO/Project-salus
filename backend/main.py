from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from backend.database import init_db, seed_missions, get_connection

app = FastAPI(
    title="Project Salus",
    version="0.2.0",
    description="Mission Control Backend"
)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = BASE_DIR / "frontend" / "templates" / "index.html"
STATIC_DIR = BASE_DIR / "frontend" / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.on_event("startup")
async def startup():
    init_db()
    seed_missions()

@app.get("/", response_class=HTMLResponse)
async def home():
    return TEMPLATE_PATH.read_text()

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.get("/missions")
async def missions():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM missions ORDER BY id").fetchall()
    conn.close()
    return {"missions": [dict(row) for row in rows]}
