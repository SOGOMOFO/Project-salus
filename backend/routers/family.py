from typing import List, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field


router = APIRouter(prefix="/family", tags=["Family Stability"])


class FamilyAARRequest(BaseModel):
    went_well: List[str] = Field(default_factory=list)
    missed_you: List[str] = Field(default_factory=list)
    avoided_topics: List[str] = Field(default_factory=list)
    needs_this_week: List[str] = Field(default_factory=list)
    building_together: List[str] = Field(default_factory=list)


class ConflictRepairRequest(BaseModel):
    issue: str
    facts: List[str] = Field(default_factory=list)
    emotions: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    desired_repair: Optional[str] = None


class AssetProtectionReviewRequest(BaseModel):
    business_assets: List[str] = Field(default_factory=list)
    personal_assets: List[str] = Field(default_factory=list)
    debts: List[str] = Field(default_factory=list)
    legal_documents: List[str] = Field(default_factory=list)
    unclear_boundaries: List[str] = Field(default_factory=list)


def risk_level(score: int) -> str:
    if score >= 75:
        return "green"
    if score >= 50:
        return "amber"
    return "red"


@router.get("/readiness")
def family_readiness():
    return {
        "module": "Family Stability & Relationship Operating System",
        "status": "active",
        "mission": "Protect family cohesion, communication, legal clarity, and legacy readiness.",
        "standing_functions": [
            "weekly_family_aar",
            "conflict_repair_protocol",
            "resentment_detection",
            "asset_protection_review",
            "household_alignment",
        ],
        "command_standard": "The family is a mission-critical asset.",
    }


@router.post("/weekly-aar")
def weekly_family_aar(payload: FamilyAARRequest):
    risk_flags = []

    if payload.avoided_topics:
        risk_flags.append("avoided_topics_present")

    if payload.missed_you:
        risk_flags.append("relationship_repair_needed")

    if not payload.building_together:
        risk_flags.append("shared_future_not_articulated")

    score = 100
    score -= len(payload.avoided_topics) * 10
    score -= len(payload.missed_you) * 5

    if not payload.building_together:
        score -= 15

    score = max(0, min(100, score))

    return {
        "family_readiness_score": score,
        "risk_level": risk_level(score),
        "risk_flags": risk_flags,
        "recommended_actions": [
            "Choose one avoided topic for a calm discussion this week.",
            "Convert each complaint into one specific request.",
            "Identify one shared family objective for the next seven days.",
        ],
        "aar_summary": payload.model_dump(),
    }


@router.post("/conflict-repair")
def conflict_repair(payload: ConflictRepairRequest):
    return {
        "issue": payload.issue,
        "repair_protocol": [
            "State the issue without blame.",
            "Separate facts from emotions.",
            "Identify assumptions that may be driving escalation.",
            "Name the specific repair action needed.",
            "Agree on one follow-up check.",
        ],
        "facts": payload.facts,
        "emotions": payload.emotions,
        "assumptions": payload.assumptions,
        "desired_repair": payload.desired_repair,
        "recommended_language": "I want to solve this with you, not win against you.",
    }


@router.post("/asset-protection-review")
def asset_protection_review(payload: AssetProtectionReviewRequest):
    gaps = []

    if not payload.legal_documents:
        gaps.append("no_legal_documents_listed")

    if payload.unclear_boundaries:
        gaps.append("mine_yours_ours_boundaries_unclear")

    if payload.business_assets:
        gaps.append("business_assets_require_structure_review")

    return {
        "review_type": "family_asset_protection",
        "identified_gaps": gaps,
        "professional_review_note": (
            "Salus does not provide legal advice. These items may require review by "
            "an attorney, CPA, financial planner, or estate-planning professional."
        ),
        "recommended_review_areas": [
            "estate_plan",
            "trust_or_will",
            "business_operating_agreement",
            "real_estate_ownership",
            "investment_accounts",
            "military_retirement_considerations",
            "VA_disability_considerations",
            "mine_yours_ours_boundaries",
        ],
    }