from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from backend.core.subsystem_registry import get_subsystem, list_subsystems, subsystem_registry_status

from backend.core.kernel import (
    kernel_architecture,
    kernel_status,
    route_request,
)


router = APIRouter(tags=["salus-kernel"])


@router.get("/api/kernel/status")
async def kernel_status_api() -> dict[str, Any]:
    return kernel_status()


@router.get("/api/kernel/architecture")
async def kernel_architecture_api() -> dict[str, Any]:
    return kernel_architecture()




@router.get("/api/kernel/subsystems")
async def kernel_subsystems_api() -> dict[str, Any]:
    subsystems = list_subsystems()
    return {
        "status": "ok",
        "count": len(subsystems),
        "subsystems": subsystems,
    }


@router.get("/api/kernel/subsystems/{subsystem_id}")
async def kernel_subsystem_api(subsystem_id: str) -> dict[str, Any]:
    subsystem = get_subsystem(subsystem_id)

    if subsystem is None:
        raise HTTPException(status_code=404, detail="subsystem not found")

    return {
        "status": "ok",
        "subsystem": subsystem,
    }


@router.get("/api/kernel/subsystem-registry/status")
async def kernel_subsystem_registry_status_api() -> dict[str, Any]:
    return subsystem_registry_status()


@router.post("/api/kernel/route")
async def kernel_route_api(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return route_request(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/command/kernel", response_class=HTMLResponse)
async def kernel_page() -> HTMLResponse:
    return HTMLResponse("""
    <!doctype html>
    <html>
      <head><title>Project Salus — Kernel</title></head>
      <body>
        <h1>Project Salus — Kernel v0.1</h1>
        <p>Central orchestration layer for identity, memory, judgment, agents, execution, and learning.</p>

        <a href="/command/core-identity">Core Identity</a>
        <a href="/command/knowledge">Knowledge</a>
        <a href="/command/memory">Memory</a>
        <a href="/command/judgment">Judgment</a>

        <h2>Status</h2>
        <pre id="status">Loading...</pre>

        <h2>Architecture</h2>
        <pre id="architecture">Loading...</pre>

        <script>
          fetch("/api/kernel/status").then(r => r.json()).then(d => {
            document.getElementById("status").textContent = JSON.stringify(d, null, 2);
          });
          fetch("/api/kernel/architecture").then(r => r.json()).then(d => {
            document.getElementById("architecture").textContent = JSON.stringify(d, null, 2);
          });
        </script>
      </body>
    </html>
    """)
