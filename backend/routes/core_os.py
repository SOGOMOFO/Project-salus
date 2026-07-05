from typing import Any, Dict

from fastapi import APIRouter, HTTPException

from backend.services.core_os_service import (
    business_brief,
    business_status,
    command_brief,
    command_next_actions,
    command_readiness,
    command_risks,
    create_business_mission,
    create_health_checkin,
    health_brief,
    health_status,
    legacy_brief,
    legacy_status,
    reset_core_os_data,
)


router = APIRouter(tags=["Project Salus Core OS"])


@router.post("/api/core-os/reset")
def core_os_reset(payload: Dict[str, Any]):
    if payload.get("confirmation") != "RESET_CORE_OS_DEV_DATA":
        raise HTTPException(status_code=400, detail="Reset confirmation required.")

    return {
        "status": "ok",
        "reset": True,
        "cleared": reset_core_os_data(),
    }


@router.get("/api/command/brief")
def api_command_brief():
    return command_brief()


@router.get("/api/command/readiness")
def api_command_readiness():
    return command_readiness()


@router.get("/api/command/risks")
def api_command_risks():
    return command_risks()


@router.get("/api/command/next-actions")
def api_command_next_actions():
    return command_next_actions()


@router.get("/health/status")
def api_health_status():
    return health_status()


@router.post("/health/check-in")
def api_health_check_in(payload: Dict[str, Any]):
    return {
        "status": "ok",
        "health_checkin": create_health_checkin(payload),
    }


@router.get("/health/brief")
def api_health_brief():
    return health_brief()


@router.get("/business/status")
def api_business_status():
    return business_status()


@router.post("/business/mission")
def api_business_mission(payload: Dict[str, Any]):
    return {
        "status": "ok",
        "business_mission": create_business_mission(payload),
    }


@router.get("/business/brief")
def api_business_brief():
    return business_brief()


@router.get("/legacy/status")
def api_legacy_status():
    return legacy_status()


@router.get("/legacy/brief")
def api_legacy_brief():
    return legacy_brief()


# --- Non-conflicting Core OS command aliases ---
@router.get("/api/core-os/command/brief")
def api_core_os_command_brief():
    return command_brief()


@router.get("/api/core-os/command/readiness")
def api_core_os_command_readiness():
    return command_readiness()


@router.get("/api/core-os/command/risks")
def api_core_os_command_risks():
    return command_risks()


@router.get("/api/core-os/command/next-actions")
def api_core_os_command_next_actions():
    return command_next_actions()
