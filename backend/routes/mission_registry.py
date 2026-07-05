from typing import List, Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.mission_registry_service import (
    MISSION_STATUSES,
    add_registry_aar,
    build_registry_dashboard,
    create_registry_mission,
    get_mission,
    list_missions,
    reset_registry,
    update_registry_status,
)


router = APIRouter(prefix="/mission-registry", tags=["Mission Registry"])


MissionStatus = Literal[
    "planned",
    "active",
    "blocked",
    "completed",
    "paused",
    "cancelled",
]


class RegistryMissionCreateRequest(BaseModel):
    title: str = Field(..., min_length=1)
    objective: str = Field(..., min_length=1)
    source: str = "manual"
    owner: str = ""
    status: MissionStatus = "planned"
    deadline: str = ""

    strategic_fit: int = Field(5, ge=0, le=10)
    roi: int = Field(5, ge=0, le=10)
    urgency: int = Field(5, ge=0, le=10)
    risk: int = Field(5, ge=0, le=10)
    difficulty: int = Field(5, ge=0, le=10)
    opportunity_cost: int = Field(5, ge=0, le=10)

    success_criteria: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    next_actions: List[str] = Field(default_factory=list)


class RegistryStatusUpdateRequest(BaseModel):
    mission_id: str = Field(..., min_length=1)
    status: MissionStatus
    progress_notes: List[str] = Field(default_factory=list)
    completed_criteria: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)


class RegistryAARRequest(BaseModel):
    mission_id: str = Field(..., min_length=1)
    title: str = "Untitled Mission"
    effectiveness_score: int = Field(5, ge=0, le=10)
    what_went_well: List[str] = Field(default_factory=list)
    what_failed: List[str] = Field(default_factory=list)
    lessons_learned: List[str] = Field(default_factory=list)
    next_actions: List[str] = Field(default_factory=list)
    doctrine_updates: List[str] = Field(default_factory=list)


@router.get("/framework")
def get_mission_registry_framework():
    return {
        "name": "Project Salus Mission Registry & Persistence V1",
        "purpose": "Persist missions, statuses, blockers, progress notes, AARs, and mission dashboard signals.",
        "statuses": MISSION_STATUSES,
        "storage": "json",
        "records": [
            "missions",
            "aars",
        ],
    }


@router.post("/create")
def create_mission(request: RegistryMissionCreateRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return create_registry_mission(payload)


@router.get("/list")
def list_registry_missions(
    status: Optional[str] = None,
    owner: Optional[str] = None,
    priority: Optional[str] = None,
):
    return list_missions(status=status, owner=owner, priority=priority)


@router.get("/{mission_id}")
def read_registry_mission(mission_id: str):
    return get_mission(mission_id)


@router.post("/update-status")
def update_status(request: RegistryStatusUpdateRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return update_registry_status(payload)


@router.post("/aar")
def add_aar(request: RegistryAARRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return add_registry_aar(payload)


@router.get("/dashboard/summary")
def dashboard():
    return build_registry_dashboard()


@router.post("/reset")
def reset():
    return reset_registry()
