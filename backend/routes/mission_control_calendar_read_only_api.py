from __future__ import annotations

from fastapi import APIRouter

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/calendar-read-only")
def api_calendar_read_only_state():
    return mc_service.get_calendar_read_only_connector_state()


@router.get("/api/mission-control/calendar-read-only/capabilities")
def api_calendar_read_only_capabilities():
    return {
        "status": "ok",
        "connector_key": "calendar_read_only",
        "capabilities": mc_service.list_calendar_read_only_capabilities(),
    }


@router.post("/api/mission-control/calendar-read-only/evaluate")
def api_calendar_read_only_evaluate(
    action_type: str,
    risk_level: str = "medium",
):
    return mc_service.evaluate_calendar_read_only_request(
        action_type=action_type,
        risk_level=risk_level,
    )


@router.get("/api/mission-control/calendar-read-only/activation-plan")
def api_calendar_read_only_activation_plan():
    return mc_service.get_calendar_read_only_activation_plan()
