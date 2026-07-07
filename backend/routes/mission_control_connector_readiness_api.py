from __future__ import annotations

from fastapi import APIRouter

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/connector-readiness")
def api_connector_readiness_registry():
    return mc_service.get_connector_readiness_registry_state()


@router.get("/api/mission-control/connector-readiness/{connector_key}")
def api_connector_readiness(connector_key: str):
    return mc_service.get_connector_readiness(connector_key)
