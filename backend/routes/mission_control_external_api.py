from __future__ import annotations

from fastapi import APIRouter, Request

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/state")
def api_mission_control_state():
    return mc_service.get_mission_control_state()


@router.get("/api/mission-control/readiness")
def api_mission_control_readiness():
    return mc_service.get_readiness_snapshot()


@router.get("/api/mission-control/operator-queue")
def api_operator_queue():
    return {
        "status": "ok",
        "operator_queue": mc_service.list_operator_queue(),
    }


@router.post("/api/mission-control/operator-queue")
async def api_create_operator_queue_item(request: Request):
    payload = await request.json()

    mc_service.create_operator_item(
        title=payload.get("title") or "API Operator Item",
        description=payload.get("description") or "",
        queue_type=payload.get("queue_type") or "task",
        status=payload.get("status") or "open",
        priority=payload.get("priority") or "medium",
    )

    return {
        "status": "created",
        "state": mc_service.get_readiness_snapshot(),
    }


# Static routes must come before dynamic /{item_id} routes.
@router.post("/api/mission-control/operator-queue/generate-missions")
def api_generate_missions_from_operator_queue():
    created = mc_service.generate_missions_from_queue()
    return {
        "status": "generated",
        "missions_created": created,
        "state": mc_service.get_readiness_snapshot(),
    }


@router.post("/api/mission-control/operator-queue/cleanup")
def api_cleanup_operator_queue():
    deleted = mc_service.cleanup_done_operator_items()
    return {
        "status": "cleaned",
        "deleted": deleted,
        "state": mc_service.get_readiness_snapshot(),
    }


@router.post("/api/mission-control/operator-queue/{item_id}/status/{status}")
def api_update_operator_queue_status(item_id: int, status: str):
    updated = mc_service.update_operator_item_status(item_id, status)
    return {
        "status": "updated" if updated else "ignored",
        "item_id": item_id,
        "requested_status": status,
    }


@router.post("/api/mission-control/operator-queue/{item_id}/convert-to-mission")
def api_convert_operator_queue_item_to_mission(item_id: int):
    converted = mc_service.convert_operator_item_to_mission(item_id)
    return {
        "status": "converted" if converted else "not_found",
        "item_id": item_id,
        "state": mc_service.get_readiness_snapshot(),
    }


@router.post("/api/mission-control/mission")
async def api_create_mission(request: Request):
    payload = await request.json()
    mc_service.create_mission_from_payload(payload)
    return {
        "status": "created",
        "state": mc_service.get_readiness_snapshot(),
    }


@router.post("/api/mission-control/sitrep")
async def api_create_sitrep(request: Request):
    payload = await request.json()
    mc_service.create_sitrep_from_payload(payload)
    return {
        "status": "created",
        "state": mc_service.get_readiness_snapshot(),
    }


@router.post("/api/mission-control/aar")
async def api_create_aar(request: Request):
    payload = await request.json()
    mc_service.create_aar_from_payload(payload)
    return {
        "status": "created",
        "state": mc_service.get_readiness_snapshot(),
    }


@router.post("/api/mission-control/commander-brief")
def api_generate_commander_brief():
    brief = mc_service.create_commander_brief()
    return {
        "status": "created",
        "brief": brief,
        "latest": mc_service.get_latest_commander_brief(),
    }


@router.get("/api/mission-control/commander-brief/latest")
def api_latest_commander_brief():
    return {
        "status": "ok",
        "latest": mc_service.get_latest_commander_brief(),
    }
