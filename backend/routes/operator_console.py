from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from backend.services.operator_console_service import (
    MODULE_CARDS,
    build_action_queue,
    build_health_check,
    build_module_cards,
    build_operator_overview,
    build_smoke_targets,
)


router = APIRouter(prefix="/operator-console", tags=["Operator Console"])


class OperatorOverviewRequest(BaseModel):
    commander_intent: Optional[str] = None


@router.get("/framework")
def framework():
    return {
        "name": "Project Salus Operator Console V1",
        "purpose": "Provide one command-facing operating picture for modules, missions, doctrine, workflows, risks, and next action.",
        "tracked_modules": len(MODULE_CARDS),
        "outputs": [
            "overview",
            "action_queue",
            "module_cards",
            "health_check",
            "smoke_targets",
        ],
    }


@router.post("/overview")
def overview(request: OperatorOverviewRequest):
    payload = request.model_dump() if hasattr(request, "model_dump") else request.dict()
    return build_operator_overview(payload)


@router.get("/action-queue")
def action_queue():
    return build_action_queue()


@router.get("/modules")
def modules():
    return build_module_cards()


@router.get("/health")
def health():
    return build_health_check()


@router.get("/smoke-targets")
def smoke_targets():
    return build_smoke_targets()
