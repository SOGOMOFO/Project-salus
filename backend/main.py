from fastapi import FastAPI, Request, HTTPException, Header
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import os

from backend.database import init_db, seed_data, get_connection

SALUS_PASSPHRASE = os.getenv("SALUS_PASSPHRASE", "salus-secure")

app = FastAPI(
    title="Project Salus",
    version="0.4.0",
    description="Mission Control Backend with Security Layer"
)

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = BASE_DIR / "frontend" / "templates" / "index.html"
STATIC_DIR = BASE_DIR / "frontend" / "static"

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


def verify_passphrase(x_salus_passphrase: str | None):
    if x_salus_passphrase != SALUS_PASSPHRASE:
        raise HTTPException(status_code=401, detail="Unauthorized access denied")


@app.on_event("startup")
async def startup():
    init_db()
    seed_data()


@app.get("/", response_class=HTMLResponse)
async def home():
    return TEMPLATE_PATH.read_text()


@app.get("/health")
async def health():
    return {"status": "healthy", "version": "0.4.0"}


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