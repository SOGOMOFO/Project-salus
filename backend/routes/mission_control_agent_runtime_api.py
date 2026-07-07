from __future__ import annotations

from fastapi import APIRouter, Request

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/agent-runtime")
def api_agent_runtime_state():
    return mc_service.get_agent_runtime_state()


@router.get("/api/mission-control/agent-runtime/events")
def api_agent_runtime_events():
    return {
        "status": "ok",
        "events": mc_service.list_agent_runtime_events(),
    }


@router.post("/api/mission-control/agent-runtime/run-next")
def api_run_next_agent_task():
    return mc_service.run_next_agent_task(actor="api_runtime")


@router.post("/api/mission-control/agent-runtime/run-batch")
async def api_run_agent_runtime_batch(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    return mc_service.run_agent_runtime_batch(
        limit=int(payload.get("limit") or 5),
        actor=payload.get("actor") or "api_runtime",
    )


@router.post("/api/mission-control/agent-runtime/tasks/{task_id}/start")
def api_start_agent_task_runtime(task_id: int):
    return mc_service.start_agent_task_runtime(task_id, actor="api_runtime")


@router.post("/api/mission-control/agent-runtime/tasks/{task_id}/complete")
async def api_finish_agent_task_runtime(task_id: int, request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    return mc_service.finish_agent_task_runtime(
        task_id=task_id,
        result=payload.get("result") or payload,
        actor=payload.get("actor") or "api_runtime",
        final_status=payload.get("final_status") or "completed",
    )


@router.post("/api/mission-control/agent-runtime/tasks/{task_id}/run")
def api_run_agent_task_once(task_id: int):
    return mc_service.run_agent_task_once(task_id, actor="api_runtime")
