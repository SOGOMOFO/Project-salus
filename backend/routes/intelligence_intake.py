from typing import List, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.intelligence_intake_service import (
    EVIDENCE_LEVELS,
    ROUTES,
    SOURCE_TYPES,
    TRIAGE_RECOMMENDATIONS,
    batch_triage,
    triage_intelligence,
)


router = APIRouter(prefix="/intelligence-intake", tags=["Intelligence Intake"])


SourceType = Literal[
    "video",
    "podcast",
    "article",
    "book",
    "social_post",
    "research_paper",
    "conversation",
    "internal_note",
    "file",
    "other",
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


class IntelligenceItemRequest(BaseModel):
    title: str = Field(..., min_length=1)
    summary: str = ""
    source_type: SourceType = "other"
    source_url: str = ""
    author_credentials: str = ""
    citations: List[str] = Field(default_factory=list)
    claims: List[str] = Field(default_factory=list)
    topics: List[str] = Field(default_factory=list)
    evidence_level: EvidenceLevel = "unverified_claim"

    owner: str = "Kyle"
    strategic_fit: int = Field(5, ge=0, le=10)
    relevance: int = Field(5, ge=0, le=10)
    actionability: int = Field(5, ge=0, le=10)
    novelty: int = Field(5, ge=0, le=10)
    source_trust: int = Field(5, ge=0, le=10)
    roi: int = Field(5, ge=0, le=10)
    urgency: int = Field(5, ge=0, le=10)
    risk: int = Field(5, ge=0, le=10)
    difficulty: int = Field(5, ge=0, le=10)
    opportunity_cost: int = Field(5, ge=0, le=10)


class BatchIntakeRequest(BaseModel):
    items: List[IntelligenceItemRequest] = Field(default_factory=list)


@router.get("/framework")
def get_intelligence_intake_framework():
    return {
        "name": "Project Salus Intelligence Intake & Triage V1",
        "purpose": "Classify raw information before it becomes action, doctrine, or distraction.",
        "source_types": SOURCE_TYPES,
        "evidence_levels": EVIDENCE_LEVELS,
        "routes": ROUTES,
        "recommendations": TRIAGE_RECOMMENDATIONS,
        "core_rule": "Information is not action until verified, routed, and converted into an executable or reviewable object.",
    }


@router.post("/triage")
def triage(request: IntelligenceItemRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return triage_intelligence(payload)


@router.post("/batch-triage")
def batch(request: BatchIntakeRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    payload["items"] = [
        item.model_dump() if hasattr(item, "model_dump") else item.dict()
        for item in request.items
    ]

    return batch_triage(payload)
