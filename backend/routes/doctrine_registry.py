from typing import List, Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.doctrine_registry_service import (
    DOCTRINE_CATEGORIES,
    DOCTRINE_STATUSES,
    EVIDENCE_LEVELS,
    build_doctrine_dashboard,
    create_doctrine_record,
    create_lesson_record,
    get_doctrine,
    list_doctrine,
    list_lessons,
    reset_registry,
    update_doctrine_status,
)


router = APIRouter(prefix="/doctrine-registry", tags=["Doctrine Registry"])


DoctrineStatus = Literal[
    "proposed",
    "active",
    "needs_review",
    "retired",
]

DoctrineCategory = Literal[
    "strategy",
    "critical_thinking",
    "ai_governance",
    "wealth",
    "family",
    "health",
    "learning",
    "mission_execution",
    "echo_seven",
    "security",
    "legacy",
    "general",
]

EvidenceLevel = Literal[
    "verified_fact",
    "strong_evidence",
    "expert_opinion",
    "emerging_theory",
    "ai_generated_pattern",
    "speculation",
    "unverified_claim",
]

Severity = Literal[
    "low",
    "medium",
    "high",
    "critical",
]


class DoctrineCreateRequest(BaseModel):
    title: str = Field(..., min_length=1)
    statement: str = Field(..., min_length=1)
    category: DoctrineCategory = "general"
    status: DoctrineStatus = "proposed"
    evidence_level: EvidenceLevel = "unverified_claim"
    source: str = "manual"
    rationale: str = ""
    triggers: List[str] = Field(default_factory=list)
    rules: List[str] = Field(default_factory=list)
    risks_if_ignored: List[str] = Field(default_factory=list)
    review_notes: List[str] = Field(default_factory=list)
    confidence_score: int = Field(5, ge=0, le=10)


class DoctrineStatusUpdateRequest(BaseModel):
    doctrine_id: str = Field(..., min_length=1)
    status: DoctrineStatus
    review_note: str = ""


class LessonCreateRequest(BaseModel):
    title: str = Field(..., min_length=1)
    lesson: str = Field(..., min_length=1)
    source: str = "manual"
    category: DoctrineCategory = "general"
    mission_id: str = ""
    severity: Severity = "medium"
    recommended_doctrine_update: str = ""
    action_items: List[str] = Field(default_factory=list)


@router.get("/framework")
def get_doctrine_registry_framework():
    return {
        "name": "Project Salus Doctrine Registry & Learning Loop V1",
        "purpose": "Persist doctrine, lessons learned, review status, and operating-rule updates.",
        "statuses": DOCTRINE_STATUSES,
        "categories": DOCTRINE_CATEGORIES,
        "evidence_levels": EVIDENCE_LEVELS,
        "records": [
            "doctrine",
            "lessons",
        ],
    }


@router.get("/dashboard")
def dashboard():
    return build_doctrine_dashboard()


@router.post("/reset")
def reset():
    return reset_registry()


@router.post("/create")
def create_doctrine(request: DoctrineCreateRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return create_doctrine_record(payload)


@router.get("/list")
def list_records(
    category: Optional[str] = None,
    status: Optional[str] = None,
    evidence_level: Optional[str] = None,
):
    return list_doctrine(
        category=category,
        status=status,
        evidence_level=evidence_level,
    )


@router.post("/update-status")
def update_status(request: DoctrineStatusUpdateRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return update_doctrine_status(payload)


@router.post("/lesson")
def create_lesson(request: LessonCreateRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return create_lesson_record(payload)


@router.get("/lessons")
def lessons(category: Optional[str] = None, severity: Optional[str] = None):
    return list_lessons(category=category, severity=severity)


@router.get("/{doctrine_id}")
def read_doctrine(doctrine_id: str):
    return get_doctrine(doctrine_id)
