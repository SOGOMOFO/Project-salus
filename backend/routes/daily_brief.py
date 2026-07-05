from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.daily_brief_service import READINESS_AREAS, generate_daily_brief


router = APIRouter(prefix="/daily-brief-v2", tags=["Daily Brief V2"])


class DailyBriefRequest(BaseModel):
    date: Optional[str] = None
    commander_intent: Optional[str] = None
    top_objectives: List[str] = Field(default_factory=list)
    active_risks: List[str] = Field(default_factory=list)
    constraints: List[str] = Field(default_factory=list)
    decisions_pending: List[str] = Field(default_factory=list)
    ai_tools_requiring_review: List[str] = Field(default_factory=list)
    wealth_flags: List[str] = Field(default_factory=list)
    echo_seven_targets: List[str] = Field(default_factory=list)
    family_focus: List[str] = Field(default_factory=list)
    health_focus: List[str] = Field(default_factory=list)
    learning_focus: List[str] = Field(default_factory=list)


@router.get("/framework")
def get_daily_brief_framework():
    return {
        "name": "Project Salus Daily Commander Brief V2",
        "purpose": "Convert risks, objectives, governance signals, wealth signals, and execution priorities into a ranked daily brief.",
        "readiness_areas": READINESS_AREAS,
        "required_logic": [
            "rank_priorities",
            "surface_risks",
            "identify_constraints",
            "connect_to_decision_firewall",
            "connect_to_ai_governance",
            "connect_to_wealth_os",
            "connect_to_echo_seven_offer",
        ],
    }


@router.post("/generate")
def generate_brief(request: DailyBriefRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return generate_daily_brief(payload)
