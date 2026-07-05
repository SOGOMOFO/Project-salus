from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.command_center_service import (
    COMMAND_MODULES,
    build_command_dashboard,
    build_module_health,
    build_morning_brief,
)


router = APIRouter(prefix="/command-center", tags=["Command Center"])


class CommandCenterRequest(BaseModel):
    commander_intent: Optional[str] = None
    enabled_modules: List[str] = Field(default_factory=list)
    reported_risks: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    ai_tools_requiring_review: List[str] = Field(default_factory=list)
    wealth_flags: List[str] = Field(default_factory=list)
    open_decisions: List[str] = Field(default_factory=list)
    echo_seven_targets: List[str] = Field(default_factory=list)
    manual_readiness_score: Optional[int] = Field(default=None, ge=0, le=100)


@router.get("/framework")
def get_command_center_framework():
    return {
        "name": "Project Salus Command Center Orchestrator V1",
        "purpose": "Unify modules, missions, risks, readiness, and priority actions into one command view.",
        "modules": COMMAND_MODULES,
        "outputs": [
            "dashboard",
            "morning_brief",
            "module_health",
            "priority_stack",
            "risk_register",
        ],
    }


@router.post("/dashboard")
def dashboard(request: CommandCenterRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return build_command_dashboard(payload)


@router.post("/morning-brief")
def morning_brief(request: CommandCenterRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return build_morning_brief(payload)


@router.post("/module-health")
def module_health(request: CommandCenterRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return build_module_health(payload)
