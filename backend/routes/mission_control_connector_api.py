from __future__ import annotations

from fastapi import APIRouter, Request

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/connectors")
def api_connector_registry_state():
    return mc_service.get_connector_registry_state()


@router.post("/api/mission-control/connectors")
async def api_upsert_connector(request: Request):
    payload = await request.json()
    return {
        "status": "saved",
        "connector": mc_service.upsert_connector_from_payload(payload),
    }


@router.get("/api/mission-control/connectors/events")
def api_connector_events():
    return {
        "status": "ok",
        "events": mc_service.list_connector_events(),
    }


@router.get("/api/mission-control/connectors/{connector_key}")
def api_get_connector(connector_key: str):
    connector = mc_service.get_connector(connector_key)
    return {
        "status": "ok" if connector else "not_found",
        "connector": connector,
    }


@router.post("/api/mission-control/connectors/{connector_key}/status/{status}")
async def api_update_connector_status(connector_key: str, status: str, request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    connector = mc_service.update_connector_status(
        connector_key=connector_key,
        status=status,
        detail=payload.get("detail") or "",
        actor=payload.get("actor") or "api",
    )

    return {
        "status": "updated" if connector.get("connector_key") else connector.get("status"),
        "connector": connector,
    }


@router.post("/api/mission-control/connectors/{connector_key}/enable")
def api_enable_connector(connector_key: str):
    connector = mc_service.set_connector_enabled(connector_key, True, actor="api")
    return {
        "status": "enabled" if connector.get("connector_key") else connector.get("status"),
        "connector": connector,
    }


@router.post("/api/mission-control/connectors/{connector_key}/disable")
def api_disable_connector(connector_key: str):
    connector = mc_service.set_connector_enabled(connector_key, False, actor="api")
    return {
        "status": "disabled" if connector.get("connector_key") else connector.get("status"),
        "connector": connector,
    }
