from __future__ import annotations

from fastapi import APIRouter, Request

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/firewall")
def api_firewall_state():
    return mc_service.get_external_action_firewall_state()


@router.post("/api/mission-control/firewall/classify")
async def api_classify_external_action(request: Request):
    payload = await request.json()
    return mc_service.classify_external_action(
        connector_key=payload.get("connector_key") or "unknown",
        action_type=payload.get("action_type") or "unknown_action",
        payload=payload.get("payload") or {},
    )


@router.get("/api/mission-control/firewall/actions")
def api_list_external_actions():
    return {
        "status": "ok",
        "actions": mc_service.list_external_actions(),
    }


@router.post("/api/mission-control/firewall/actions")
async def api_create_external_action(request: Request):
    payload = await request.json()
    return {
        "status": "created",
        "action": mc_service.create_external_action_request(payload),
    }


@router.get("/api/mission-control/firewall/actions/{action_id}")
def api_get_external_action(action_id: int):
    action = mc_service.get_external_action(action_id)
    return {
        "status": "ok" if action else "not_found",
        "action": action,
    }


@router.post("/api/mission-control/firewall/actions/{action_id}/approve")
def api_approve_external_action(action_id: int):
    return mc_service.approve_external_action(action_id, actor="api")


@router.post("/api/mission-control/firewall/actions/{action_id}/reject")
async def api_reject_external_action(action_id: int, request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    return mc_service.reject_external_action(
        action_id=action_id,
        reason=payload.get("reason") or "Rejected through API.",
        actor=payload.get("actor") or "api",
    )


@router.post("/api/mission-control/firewall/actions/{action_id}/execute-placeholder")
def api_execute_external_action_placeholder(action_id: int):
    return mc_service.execute_external_action_placeholder(action_id, actor="api")


@router.get("/api/mission-control/firewall/events")
def api_external_action_events():
    return {
        "status": "ok",
        "events": mc_service.list_external_action_events(),
    }
