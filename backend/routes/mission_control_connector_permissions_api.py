from __future__ import annotations

from fastapi import APIRouter

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/connector-permissions")
def api_connector_permissions_state():
    return mc_service.get_connector_permission_policy_state()


@router.get("/api/mission-control/connector-permissions/{connector_key}")
def api_connector_permission_profile(connector_key: str):
    profile = mc_service.get_connector_permission_profile(connector_key)
    return profile or {"status": "not_found", "connector_key": connector_key}


@router.post("/api/mission-control/connector-permissions/evaluate")
def api_connector_permission_evaluate(
    connector_key: str,
    action_type: str,
    risk_level: str = "low",
):
    return mc_service.evaluate_connector_permission(
        connector_key=connector_key,
        action_type=action_type,
        risk_level=risk_level,
    )
