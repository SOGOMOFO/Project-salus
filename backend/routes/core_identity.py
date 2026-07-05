from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse

from backend.services.core_identity_service import (
    core_identity_bundle,
    core_identity_status,
    read_doctrine_file,
)


router = APIRouter(tags=["core-identity"])


@router.get("/api/core-identity/status")
async def core_identity_status_api() -> dict[str, Any]:
    return core_identity_status()


@router.get("/api/core-identity")
async def core_identity_bundle_api() -> dict[str, Any]:
    return core_identity_bundle()


@router.get("/api/core-identity/doctrine/{key}", response_class=PlainTextResponse)
async def core_identity_doctrine_api(key: str) -> PlainTextResponse:
    try:
        item = read_doctrine_file(key)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="doctrine file not found") from exc

    if not item["exists"]:
        raise HTTPException(status_code=404, detail="doctrine file missing")

    return PlainTextResponse(content=item["content"])


@router.get("/command/core-identity", response_class=HTMLResponse)
async def core_identity_page() -> HTMLResponse:
    return HTMLResponse("""
    <!doctype html>
    <html>
      <head><title>Project Salus — Core Identity</title></head>
      <body>
        <h1>Project Salus — Core Identity</h1>
        <p>Human Judgment System for the Intelligence Age.</p>
        <a href="/command/knowledge">Knowledge</a>
        <a href="/command/memory">Memory</a>
        <a href="/command/judgment">Judgment</a>
        <a href="/command/teaching">Teaching</a>
        <a href="/command/agents">Agents</a>
        <a href="/command/database">Database</a>
        <pre id="status">Loading...</pre>
        <script>
          fetch("/api/core-identity/status").then(r => r.json()).then(d => {
            document.getElementById("status").textContent = JSON.stringify(d, null, 2);
          });
        </script>
      </body>
    </html>
    """)
