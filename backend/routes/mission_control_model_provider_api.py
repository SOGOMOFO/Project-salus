from __future__ import annotations

from fastapi import APIRouter, Request

from backend import mission_control_service as mc_service


router = APIRouter()


@router.get("/api/mission-control/model-providers")
def api_model_provider_state():
    return mc_service.get_model_provider_state()


@router.get("/api/mission-control/model-providers/providers")
def api_list_model_providers():
    return {
        "status": "ok",
        "providers": mc_service.list_model_providers(),
    }


@router.post("/api/mission-control/model-providers/providers")
async def api_upsert_model_provider(request: Request):
    payload = await request.json()
    return {
        "status": "saved",
        "provider": mc_service.upsert_model_provider_from_payload(payload),
    }


@router.get("/api/mission-control/model-providers/routes")
def api_list_model_routes():
    return {
        "status": "ok",
        "routes": mc_service.list_model_routes(),
    }


@router.post("/api/mission-control/model-providers/routes")
async def api_upsert_model_route(request: Request):
    payload = await request.json()
    return {
        "status": "saved",
        "route": mc_service.upsert_model_route_from_payload(payload),
    }


@router.get("/api/mission-control/model-providers/reasoning")
def api_list_reasoning_requests():
    return {
        "status": "ok",
        "requests": mc_service.list_reasoning_requests(),
    }


@router.post("/api/mission-control/model-providers/reasoning")
async def api_create_reasoning_request(request: Request):
    payload = await request.json()
    return {
        "status": "created",
        "request": mc_service.create_reasoning_request(payload),
    }


@router.get("/api/mission-control/model-providers/reasoning/{request_id}")
def api_get_reasoning_request(request_id: int):
    reasoning = mc_service.get_reasoning_request(request_id)
    return {
        "status": "ok" if reasoning else "not_found",
        "request": reasoning,
    }
