from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from backend.core.context_packet import build_context_packet, context_packet_status
from backend.core.response_planner import build_response_plan, response_planner_status
from backend.core.execution_gate import evaluate_execution_gate, execution_gate_status
from backend.core.learning_capture import capture_learning, get_learning_record, learning_capture_status, list_learning_records
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




@router.get("/api/kernel/context/status")
async def kernel_context_status_api() -> dict[str, Any]:
    return context_packet_status()


@router.post("/api/kernel/context")
async def kernel_context_api(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return build_context_packet(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc




@router.get("/api/kernel/plan/status")
async def kernel_plan_status_api() -> dict[str, Any]:
    return response_planner_status()


@router.post("/api/kernel/plan")
async def kernel_plan_api(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return build_response_plan(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc




@router.get("/api/kernel/execution-gate/status")
async def kernel_execution_gate_status_api() -> dict[str, Any]:
    return execution_gate_status()


@router.post("/api/kernel/execution-gate")
async def kernel_execution_gate_api(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return evaluate_execution_gate(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc




@router.get("/api/kernel/learning-capture/status")
async def kernel_learning_capture_status_api() -> dict[str, Any]:
    return learning_capture_status()


@router.post("/api/kernel/learning-capture")
async def kernel_learning_capture_api(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        record = capture_learning(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return {
        "status": "ok",
        "record": record,
    }


@router.get("/api/kernel/learning-capture/records")
async def kernel_learning_capture_records_api(
    outcome: str | None = None,
    query: str | None = None,
    tag: str | None = None,
) -> dict[str, Any]:
    records = list_learning_records(outcome=outcome, query=query, tag=tag)

    return {
        "status": "ok",
        "count": len(records),
        "records": records,
    }


@router.get("/api/kernel/learning-capture/records/{record_id}")
async def kernel_learning_capture_record_api(record_id: str) -> dict[str, Any]:
    record = get_learning_record(record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="learning record not found")

    return {
        "status": "ok",
        "record": record,
    }


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
