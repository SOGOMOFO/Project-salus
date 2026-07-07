from __future__ import annotations

from fastapi import APIRouter, Query

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/connector-activation-gate")
def api_connector_activation_gate_state():
    return mc_service.get_connector_activation_gate_state()


@router.post("/api/mission-control/connector-activation-gate/evaluate")
def api_connector_activation_gate_evaluate(
    connector_key: str,
    requested_controls: list[str] = Query(default=[]),
):
    return mc_service.evaluate_connector_activation_gate(
        connector_key=connector_key,
        requested_controls=requested_controls,
    )


@router.post("/api/mission-control/connector-activation-gate/request")
def api_connector_activation_request(
    connector_key: str,
    requested_controls: list[str] = Query(default=[]),
):
    return mc_service.create_connector_activation_request(
        connector_key=connector_key,
        requested_controls=requested_controls,
    )
