from typing import Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.decision_firewall_service import evaluate_decision

router = APIRouter(prefix="/decision-firewall", tags=["Decision Firewall"])

EvidenceType = Literal[
    "verified_fact",
    "strong_evidence",
    "expert_opinion",
    "emerging_theory",
    "ai_generated_pattern",
    "speculation",
    "unverified_claim",
]

OutputType = Literal[
    "doctrine",
    "feature",
    "checklist",
    "service_offer",
    "training_module",
    "dashboard",
    "report",
    "discard",
]


class DecisionFirewallRequest(BaseModel):
    title: str = Field(..., min_length=1)
    category: str = "general"
    claim: Optional[str] = None
    evidence_type: EvidenceType = "unverified_claim"
    strategic_fit: int = Field(..., ge=0, le=10)
    roi: int = Field(..., ge=0, le=10)
    difficulty: int = Field(..., ge=0, le=10)
    risk: int = Field(..., ge=0, le=10)
    opportunity_cost: int = Field(..., ge=0, le=10)
    actionability: int = Field(..., ge=0, le=10)
    output_type: OutputType
    owner: str = Field(..., min_length=1)


@router.get("/framework")
def get_decision_firewall_framework():
    return {
        "name": "Project Salus Decision Firewall",
        "purpose": "Prevent bloat, hype-chasing, weak evidence, and low-ROI distractions.",
        "recommendations": ["PURSUE", "PAUSE", "DELEGATE", "DISCARD"],
        "evidence_levels": [
            "verified_fact",
            "strong_evidence",
            "expert_opinion",
            "emerging_theory",
            "ai_generated_pattern",
            "speculation",
            "unverified_claim",
        ],
        "approved_output_types": [
            "doctrine",
            "feature",
            "checklist",
            "service_offer",
            "training_module",
            "dashboard",
            "report",
            "discard",
        ],
    }


@router.post("/evaluate")
def evaluate_decision_firewall(request: DecisionFirewallRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return evaluate_decision(payload)
