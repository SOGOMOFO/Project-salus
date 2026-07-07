from __future__ import annotations

from fastapi import APIRouter

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/dashboard")
def api_command_center_overview():
    return mc_service.get_command_center_overview()
