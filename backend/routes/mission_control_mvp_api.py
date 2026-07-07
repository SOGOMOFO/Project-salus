from __future__ import annotations

from fastapi import APIRouter, Request

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/records")
def api_list_records():
    return {
        "status": "ok",
        "records": mc_service.list_records(),
    }


@router.post("/api/mission-control/records")
async def api_create_record(request: Request):
    payload = await request.json()
    return {
        "status": "created",
        "record": mc_service.create_record_from_payload(payload),
    }


@router.get("/api/mission-control/daily-loop")
def api_list_daily_loops():
    return {
        "status": "ok",
        "daily_loops": mc_service.list_daily_loops(),
    }


@router.post("/api/mission-control/daily-loop/{loop_type}")
def api_create_daily_loop(loop_type: str):
    return {
        "status": "created",
        "daily_loop": mc_service.create_daily_loop(loop_type=loop_type, actor="api"),
    }


@router.get("/api/mission-control/export")
def api_export_command_state():
    return mc_service.export_command_state()


@router.get("/api/mission-control/mvp-readiness")
def api_local_mvp_readiness():
    return mc_service.get_local_mvp_readiness()
