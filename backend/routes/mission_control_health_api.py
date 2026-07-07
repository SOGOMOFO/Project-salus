from __future__ import annotations

from fastapi import APIRouter, Request

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/routes")
def api_mission_control_routes(request: Request):
    return {
        "status": "ok",
        "routes": mc_service.get_route_inventory(request.app),
    }


@router.get("/api/mission-control/contract")
def api_mission_control_contract(request: Request):
    return mc_service.get_mission_control_contract(request.app)


@router.get("/api/mission-control/health")
def api_mission_control_health(request: Request):
    return mc_service.get_system_health(request.app)
