from __future__ import annotations

from fastapi import APIRouter, Request

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/tool-adapters")
def api_tool_adapter_state():
    return mc_service.get_tool_adapter_state()


@router.post("/api/mission-control/tool-adapters")
async def api_upsert_tool_adapter(request: Request):
    payload = await request.json()
    return {
        "status": "saved",
        "adapter": mc_service.upsert_tool_adapter_from_payload(payload),
    }


@router.get("/api/mission-control/tool-adapters/runs")
def api_tool_adapter_runs():
    return {
        "status": "ok",
        "runs": mc_service.list_tool_adapter_runs(),
    }


@router.get("/api/mission-control/tool-adapters/{adapter_key}")
def api_get_tool_adapter(adapter_key: str):
    adapter = mc_service.get_tool_adapter(adapter_key)
    return {
        "status": "ok" if adapter else "not_found",
        "adapter": adapter,
    }


@router.post("/api/mission-control/tool-adapters/{adapter_key}/enable")
def api_enable_tool_adapter(adapter_key: str):
    adapter = mc_service.set_tool_adapter_enabled(adapter_key, True, actor="api")
    return {
        "status": "enabled" if adapter.get("adapter_key") else adapter.get("status"),
        "adapter": adapter,
    }


@router.post("/api/mission-control/tool-adapters/{adapter_key}/disable")
def api_disable_tool_adapter(adapter_key: str):
    adapter = mc_service.set_tool_adapter_enabled(adapter_key, False, actor="api")
    return {
        "status": "disabled" if adapter.get("adapter_key") else adapter.get("status"),
        "adapter": adapter,
    }


@router.post("/api/mission-control/tool-adapters/{adapter_key}/actions/{action_name}")
async def api_execute_tool_adapter_action(adapter_key: str, action_name: str, request: Request):
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    return mc_service.execute_tool_adapter_action(
        adapter_key=adapter_key,
        action_name=action_name,
        payload=payload,
        actor=payload.get("actor") or "api",
    )
