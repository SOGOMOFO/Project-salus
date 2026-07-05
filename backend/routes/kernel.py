from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from backend.core.context_packet import build_context_packet, context_packet_status
from backend.core.response_planner import build_response_plan, response_planner_status
from backend.core.execution_gate import evaluate_execution_gate, execution_gate_status
from backend.core.learning_capture import capture_learning, get_learning_record, learning_capture_status, list_learning_records
from backend.core.doctrine_enforcer import build_doctrine_check, doctrine_enforcer_status
from backend.core.orchestrator import orchestrate, orchestrator_status
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




@router.get("/api/kernel/doctrine-check/status")
async def kernel_doctrine_check_status_api() -> dict[str, Any]:
    return doctrine_enforcer_status()


@router.post("/api/kernel/doctrine-check")
async def kernel_doctrine_check_api(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return build_doctrine_check(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc




@router.get("/api/kernel/orchestrate/status")
async def kernel_orchestrate_status_api() -> dict[str, Any]:
    return orchestrator_status()


@router.post("/api/kernel/orchestrate")
async def kernel_orchestrate_api(payload: dict[str, Any]) -> dict[str, Any]:
    try:
        return orchestrate(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


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
      <head>
        <title>Project Salus — Kernel Command</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            margin: 32px;
            background: #0f172a;
            color: #e5e7eb;
          }
          h1, h2, h3 {
            color: #f8fafc;
          }
          a {
            color: #93c5fd;
            margin-right: 16px;
          }
          textarea {
            width: 100%;
            min-height: 120px;
            background: #020617;
            color: #e5e7eb;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 12px;
            font-size: 15px;
          }
          button {
            background: #2563eb;
            color: white;
            border: 0;
            border-radius: 8px;
            padding: 10px 16px;
            margin-top: 10px;
            cursor: pointer;
            font-weight: bold;
          }
          button:hover {
            background: #1d4ed8;
          }
          .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
            gap: 16px;
            margin-top: 20px;
          }
          .card {
            background: #111827;
            border: 1px solid #334155;
            border-radius: 10px;
            padding: 16px;
          }
          pre {
            white-space: pre-wrap;
            word-break: break-word;
            background: #020617;
            border: 1px solid #1e293b;
            border-radius: 8px;
            padding: 12px;
            max-height: 420px;
            overflow: auto;
          }
          .status {
            font-size: 14px;
            color: #cbd5e1;
          }
        </style>
      </head>
      <body>
        <h1>Project Salus — Kernel Command UI</h1>
        <p class="status">
          Kernel v0.9 integrates orchestration into the command interface.
          This UI plans, gates, checks doctrine, and recommends learning capture.
          It does not execute external actions.
        </p>

        <nav>
          <a href="/command/core-identity">Core Identity</a>
          <a href="/command/knowledge">Knowledge</a>
          <a href="/command/memory">Memory</a>
          <a href="/command/judgment">Judgment</a>
          <a href="/command/kernel">Kernel</a>
        </nav>

        <h2>Orchestrate Request</h2>
        <textarea id="kernelInput" placeholder="Enter a request for the Salus Kernel...">Should I submit this contract?</textarea>
        <br>
        <button onclick="runKernel()">Run Kernel Orchestration</button>

        <div class="grid">
          <div class="card">
            <h3>Kernel Status</h3>
            <pre id="status">Loading...</pre>
          </div>

          <div class="card">
            <h3>Context Packet</h3>
            <pre id="contextPacket">Waiting for orchestration...</pre>
          </div>

          <div class="card">
            <h3>Response Plan</h3>
            <pre id="responsePlan">Waiting for orchestration...</pre>
          </div>

          <div class="card">
            <h3>Execution Gate</h3>
            <pre id="executionGate">Waiting for orchestration...</pre>
          </div>

          <div class="card">
            <h3>Doctrine Check</h3>
            <pre id="doctrineCheck">Waiting for orchestration...</pre>
          </div>

          <div class="card">
            <h3>Learning Recommendation</h3>
            <pre id="learningRecommendation">Waiting for orchestration...</pre>
          </div>
        </div>

        <script>
          function pretty(data) {
            return JSON.stringify(data, null, 2);
          }

          async function loadStatus() {
            const response = await fetch("/api/kernel/status");
            const data = await response.json();
            document.getElementById("status").textContent = pretty(data);
          }

          async function runKernel() {
            const input = document.getElementById("kernelInput").value;

            const response = await fetch("/api/kernel/orchestrate", {
              method: "POST",
              headers: {"Content-Type": "application/json"},
              body: JSON.stringify({user: "Kyle", input: input})
            });

            const data = await response.json();

            if (!response.ok) {
              document.getElementById("contextPacket").textContent = pretty(data);
              return;
            }

            document.getElementById("contextPacket").textContent = pretty(data.context_packet);
            document.getElementById("responsePlan").textContent = pretty(data.response_plan);
            document.getElementById("executionGate").textContent = pretty(data.execution_gate);
            document.getElementById("doctrineCheck").textContent = pretty(data.doctrine_check);
            document.getElementById("learningRecommendation").textContent = pretty(data.learning_recommendation);
          }

          loadStatus();
        </script>
      </body>
    </html>
    """)

