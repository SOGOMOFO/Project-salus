from typing import List, Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.strategy_critical_thinking_service import (
    REASONING_LENSES,
    RECOMMENDATIONS,
    analyze_strategy,
    generate_red_team,
)


router = APIRouter(prefix="/strategy-critical-thinking", tags=["Strategy & Critical Thinking"])


EvidenceLevel = Literal[
    "verified_fact",
    "strong_evidence",
    "expert_opinion",
    "emerging_theory",
    "ai_generated_pattern",
    "speculation",
    "unverified_claim",
]


class StrategyAnalysisRequest(BaseModel):
    title: str = Field(..., min_length=1)
    objective: str = Field(..., min_length=1)
    context: Optional[str] = None
    evidence_level: EvidenceLevel = "unverified_claim"

    strategic_fit: int = Field(..., ge=0, le=10)
    roi: int = Field(..., ge=0, le=10)
    risk: int = Field(..., ge=0, le=10)
    difficulty: int = Field(..., ge=0, le=10)
    opportunity_cost: int = Field(..., ge=0, le=10)

    time_horizon: str = "one sprint"
    assumptions: List[str] = Field(default_factory=list)
    evidence_for: List[str] = Field(default_factory=list)
    evidence_against: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    alternatives: List[str] = Field(default_factory=list)
    failure_modes: List[str] = Field(default_factory=list)
    stakeholders: List[str] = Field(default_factory=list)


class RedTeamRequest(BaseModel):
    title: str = Field(..., min_length=1)
    objective: str = ""
    assumptions: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)
    failure_modes: List[str] = Field(default_factory=list)
    evidence_against: List[str] = Field(default_factory=list)


@router.get("/framework")
def get_strategy_critical_thinking_framework():
    return {
        "name": "Project Salus Strategy & Critical Thinking Directorate",
        "purpose": "Force major ideas through disciplined reasoning before commitment.",
        "recommendations": RECOMMENDATIONS,
        "reasoning_lenses": REASONING_LENSES,
        "core_questions": [
            "What is the actual objective?",
            "What assumptions are being made?",
            "What evidence supports this?",
            "What evidence argues against it?",
            "What could go wrong?",
            "What are the second- and third-order effects?",
            "What is the opportunity cost?",
            "What is the smallest reversible test?",
            "What would make us stop?",
        ],
    }


@router.post("/analyze")
def analyze(request: StrategyAnalysisRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return analyze_strategy(payload)


@router.post("/red-team")
def red_team(request: RedTeamRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return generate_red_team(payload)
