from typing import List, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.ai_governance_service import REQUIRED_CONTROLS, assess_ai_tool


router = APIRouter(prefix="/ai-governance", tags=["AI Governance"])


AccessLevel = Literal["none", "read", "write", "execute", "admin"]
AutonomyLevel = Literal["assistive", "recommends", "acts_with_approval", "acts_autonomously"]
BusinessImpact = Literal["low", "medium", "high"]


class AIToolAssessmentRequest(BaseModel):
    tool_name: str = Field(..., min_length=1)
    purpose: str = Field(..., min_length=1)
    data_types: List[str] = []
    access_level: AccessLevel = "none"
    autonomy_level: AutonomyLevel = "assistive"
    external_connections: List[str] = []
    business_impact: BusinessImpact = "low"
    human_approval_required: bool = False
    audit_logging: bool = False
    kill_switch: bool = False
    model_fallback: bool = False
    output_verification: bool = False


@router.get("/framework")
def get_ai_governance_framework():
    return {
        "name": "Project Salus AI Governance Checklist",
        "purpose": "Control AI tool risk before deployment or expanded use.",
        "core_doctrine": "No powerful AI tool or agent receives unchecked authority.",
        "required_controls": REQUIRED_CONTROLS,
        "risk_levels": ["green", "amber", "red"],
        "decisions": ["APPROVED", "APPROVED_WITH_CONTROLS", "BLOCKED_UNTIL_REMEDIATED"],
    }


@router.post("/assess-tool")
def assess_tool(request: AIToolAssessmentRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return assess_ai_tool(payload)
