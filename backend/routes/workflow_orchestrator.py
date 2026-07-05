from typing import Any, Dict

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.workflow_orchestrator_service import (
    WORKFLOW_ACTIONS,
    WORKFLOW_TYPES,
    build_workflow_dashboard,
    create_doctrine_from_candidate,
    create_mission_from_candidate,
    list_workflow_runs,
    reset_workflows,
    run_intelligence_workflow,
)


router = APIRouter(prefix="/workflow-orchestrator", tags=["Workflow Orchestrator"])


class IntelligenceWorkflowRequest(BaseModel):
    item: Dict[str, Any] = Field(default_factory=dict)
    auto_create_records: bool = True
    park_verify_items: bool = True
    create_discard_records: bool = False


class MissionCandidateCreateRequest(BaseModel):
    mission_candidate: Dict[str, Any] = Field(default_factory=dict)
    source_item: Dict[str, Any] = Field(default_factory=dict)


class DoctrineCandidateCreateRequest(BaseModel):
    doctrine_candidate: Dict[str, Any] = Field(default_factory=dict)
    source_item: Dict[str, Any] = Field(default_factory=dict)


@router.get("/framework")
def framework():
    return {
        "name": "Project Salus Workflow Orchestrator V1",
        "purpose": "Move intelligence through triage into parking lot, mission registry, or doctrine registry.",
        "workflow_types": WORKFLOW_TYPES,
        "workflow_actions": WORKFLOW_ACTIONS,
        "core_flow": [
            "intake",
            "triage",
            "route",
            "create_record",
            "review_or_execute",
        ],
    }


@router.post("/intelligence-to-action")
def intelligence_to_action(request: IntelligenceWorkflowRequest):
    return run_intelligence_workflow(
        request.model_dump() if hasattr(request, "model_dump") else request.dict()
    )


@router.post("/create-mission-from-candidate")
def create_mission(request: MissionCandidateCreateRequest):
    return create_mission_from_candidate(
        request.model_dump() if hasattr(request, "model_dump") else request.dict()
    )


@router.post("/create-doctrine-from-candidate")
def create_doctrine(request: DoctrineCandidateCreateRequest):
    return create_doctrine_from_candidate(
        request.model_dump() if hasattr(request, "model_dump") else request.dict()
    )


@router.get("/runs")
def runs():
    return list_workflow_runs()


@router.get("/dashboard")
def dashboard():
    return build_workflow_dashboard()


@router.post("/reset")
def reset():
    return reset_workflows()
