from __future__ import annotations

from fastapi import APIRouter, Request

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/architecture")
def api_architecture_manifest(request: Request):
    return mc_service.get_project_salus_architecture_manifest(request.app)


@router.get("/api/mission-control/system-contract")
def api_project_salus_contract(request: Request):
    return mc_service.get_project_salus_contract(request.app)
