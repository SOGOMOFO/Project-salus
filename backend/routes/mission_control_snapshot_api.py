from __future__ import annotations

from fastapi import APIRouter, Request

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/snapshots")
def api_list_snapshots():
    return mc_service.get_snapshot_system_state()


@router.post("/api/mission-control/snapshots")
async def api_create_snapshot(request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    return mc_service.create_system_snapshot(
        label=payload.get("label") or "api_snapshot",
        actor=payload.get("actor") or "api",
    )


@router.get("/api/mission-control/snapshots/{snapshot_name}")
def api_get_snapshot(snapshot_name: str):
    snapshot = mc_service.get_system_snapshot(snapshot_name)
    return {
        "status": "ok" if snapshot else "not_found",
        "snapshot": snapshot,
    }


@router.post("/api/mission-control/snapshots/{snapshot_name}/restore")
def api_restore_snapshot(snapshot_name: str):
    return mc_service.restore_system_snapshot(snapshot_name, actor="api")


@router.delete("/api/mission-control/snapshots/{snapshot_name}")
def api_delete_snapshot(snapshot_name: str):
    return mc_service.delete_system_snapshot(snapshot_name, actor="api")
