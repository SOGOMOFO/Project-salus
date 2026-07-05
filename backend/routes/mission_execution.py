from typing import List, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.mission_execution_service import (
    MISSION_RECOMMENDATIONS,
    MISSION_STATUSES,
    build_sprint_plan,
    create_mission,
    generate_aar,
    update_mission_status,
)


router = APIRouter(prefix="/mission-execution", tags=["Mission Execution"])


MissionStatus = Literal[
    "planned",
    "active",
    "blocked",
    "completed",
    "paused",
    "cancelled",
]


class MissionCreateRequest(BaseModel):
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


class MissionStatusUpdateRequest(BaseModel):
    mission_id: str = ""
    title: str = "Untitled Mission"
    status: MissionStatus
    progress_notes: List[str] = Field(default_factory=list)
    completed_criteria: List[str] = Field(default_factory=list)
    blockers: List[str] = Field(default_factory=list)


class SprintPlanRequest(BaseModel):
    sprint_name: str = "Unnamed Sprint"
    capacity: int = Field(5, ge=1, le=10)
    missions: List[MissionCreateRequest] = Field(default_factory=list)


class MissionAARRequest(BaseModel):
    mission_id: str = ""
    title: str = "Untitled Mission"
    effectiveness_score: int = Field(5, ge=0, le=10)
    what_went_well: List[str] = Field(default_factory=list)
    what_failed: List[str] = Field(default_factory=list)
    lessons_learned: List[str] = Field(default_factory=list)
    next_actions: List[str] = Field(default_factory=list)
    doctrine_updates: List[str] = Field(default_factory=list)


@router.get("/framework")
def get_mission_execution_framework():
    return {
        "name": "Project Salus Mission Execution Engine V1",
        "purpose": "Convert recommendations into tracked missions with owners, success criteria, blockers, status, sprint planning, and AARs.",
        "statuses": MISSION_STATUSES,
        "recommendations": MISSION_RECOMMENDATIONS,
        "required_fields": [
            "title",
            "objective",
            "owner",
            "deadline",
            "success_criteria",
            "status",
            "blockers",
            "next_actions",
        ],
    }


@router.post("/create")
def create(request: MissionCreateRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return create_mission(payload)


@router.post("/update-status")
def update_status(request: MissionStatusUpdateRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return update_mission_status(payload)


@router.post("/sprint-plan")
def sprint_plan(request: SprintPlanRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    payload["missions"] = [
        mission.model_dump() if hasattr(mission, "model_dump") else mission.dict()
        for mission in request.missions
    ]

    return build_sprint_plan(payload)


@router.post("/aar")
def aar(request: MissionAARRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return generate_aar(payload)
