from __future__ import annotations

from fastapi import APIRouter, Request

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/agent/state")
def api_agent_execution_state():
    return mc_service.get_agent_execution_state()


@router.get("/api/mission-control/agent/tasks")
def api_list_agent_tasks():
    return {
        "status": "ok",
        "tasks": mc_service.list_agent_tasks(),
    }


@router.post("/api/mission-control/agent/tasks")
async def api_create_agent_task(request: Request):
    payload = await request.json()
    task = mc_service.create_agent_task_from_payload(payload)
    return {
        "status": "created",
        "task": task,
    }


@router.get("/api/mission-control/agent/tasks/{task_id}")
def api_get_agent_task(task_id: int):
    task = mc_service.get_agent_task(task_id)
    return {
        "status": "ok" if task else "not_found",
        "task": task,
    }


@router.post("/api/mission-control/agent/tasks/{task_id}/approve")
def api_approve_agent_task(task_id: int):
    approved = mc_service.approve_agent_task(task_id, actor="commander")
    return {
        "status": "approved" if approved else "not_found",
        "task_id": task_id,
    }


@router.post("/api/mission-control/agent/tasks/{task_id}/reject")
async def api_reject_agent_task(task_id: int, request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    rejected = mc_service.reject_agent_task(
        task_id,
        actor=payload.get("actor") or "commander",
        reason=payload.get("reason") or "Rejected through API.",
    )

    return {
        "status": "rejected" if rejected else "not_found",
        "task_id": task_id,
    }


@router.post("/api/mission-control/agent/tasks/{task_id}/complete")
async def api_complete_agent_task(task_id: int, request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    result = mc_service.complete_agent_task(
        task_id,
        result=payload.get("result") or payload,
        actor=payload.get("actor") or "agent_runtime",
    )

    return result


@router.get("/api/mission-control/agent/audit-log")
def api_agent_audit_log():
    return {
        "status": "ok",
        "audit_log": mc_service.list_audit_log(),
    }


@router.get("/api/mission-control/agent/permission-gates")
def api_agent_permission_gates():
    return {
        "status": "ok",
        "permission_gates": mc_service.list_permission_gates(),
    }
