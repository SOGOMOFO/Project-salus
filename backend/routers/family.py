from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4
import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


router = APIRouter(prefix="/family", tags=["Family Stability"])


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

FAMILY_AARS_FILE = DATA_DIR / "family_weekly_aars.json"
FAMILY_ALIGNMENTS_FILE = DATA_DIR / "family_household_alignments.json"
FAMILY_ASSET_REVIEWS_FILE = DATA_DIR / "family_asset_reviews.json"


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


class HouseholdAlignmentRequest(BaseModel):
    top_family_priority: str = ""
    household_stressors: List[str] = Field(default_factory=list)
    money_topics: List[str] = Field(default_factory=list)
    parenting_topics: List[str] = Field(default_factory=list)
    schedule_conflicts: List[str] = Field(default_factory=list)
    business_impacts: List[str] = Field(default_factory=list)
    next_family_actions: List[str] = Field(default_factory=list)


class FamilyResetRequest(BaseModel):
    confirmation: str = ""


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def risk_level(score: int) -> str:
    if score >= 75:
        return "green"
    if score >= 50:
        return "amber"
    return "red"


def bounded_score(score: int) -> int:
    return max(0, min(100, score))


def dump_model(payload):
    if hasattr(payload, "model_dump"):
        return payload.model_dump()
    return payload.dict()


def read_json(path: Path, default):
    if not path.exists():
        return default

    try:
        return json.loads(path.read_text())
    except Exception:
        return default


def write_json(path: Path, data):
    path.write_text(json.dumps(data, indent=2, sort_keys=True, default=str))
    return data


def append_record(path: Path, record: Dict[str, Any]) -> Dict[str, Any]:
    records = read_json(path, [])
    records.append(record)
    write_json(path, records)
    return record


def build_weekly_aar_result(payload: FamilyAARRequest) -> Dict[str, Any]:
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

    score = bounded_score(score)

    return {
        "family_readiness_score": score,
        "risk_level": risk_level(score),
        "risk_flags": risk_flags,
        "recommended_actions": [
            "Choose one avoided topic for a calm discussion this week.",
            "Convert each complaint into one specific request.",
            "Identify one shared family objective for the next seven days.",
        ],
        "aar_summary": dump_model(payload),
    }


def build_household_alignment_result(payload: HouseholdAlignmentRequest) -> Dict[str, Any]:
    risk_flags = []

    if payload.household_stressors:
        risk_flags.append("household_stressors_present")

    if payload.money_topics:
        risk_flags.append("money_topics_present")

    if payload.schedule_conflicts:
        risk_flags.append("schedule_conflicts_present")

    if payload.business_impacts:
        risk_flags.append("business_family_tradeoffs_present")

    if not payload.next_family_actions:
        risk_flags.append("next_actions_missing")

    score = 100
    score -= len(payload.household_stressors) * 5
    score -= len(payload.money_topics) * 7
    score -= len(payload.schedule_conflicts) * 5
    score -= len(payload.business_impacts) * 5

    if not payload.top_family_priority:
        score -= 10

    if not payload.next_family_actions:
        score -= 15

    score = bounded_score(score)

    return {
        "alignment_score": score,
        "risk_level": risk_level(score),
        "risk_flags": risk_flags,
        "top_family_priority": payload.top_family_priority,
        "recommended_actions": [
            "Define the single most important household priority for the week.",
            "Assign one owner and one deadline to each family action.",
            "Separate money, parenting, schedule, and business topics before discussing solutions.",
            "Close the alignment check with one agreed next action.",
        ],
        "alignment_summary": dump_model(payload),
    }


def build_asset_review_result(payload: AssetProtectionReviewRequest) -> Dict[str, Any]:
    gaps = []

    if not payload.legal_documents:
        gaps.append("no_legal_documents_listed")

    if payload.unclear_boundaries:
        gaps.append("mine_yours_ours_boundaries_unclear")

    if payload.business_assets:
        gaps.append("business_assets_require_structure_review")

    if payload.debts:
        gaps.append("debt_obligations_should_be_reviewed")

    if payload.personal_assets and not payload.legal_documents:
        gaps.append("personal_assets_without_documented_plan")

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
            "insurance_coverage",
            "beneficiary_designations",
        ],
    }


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
            "legacy_alignment",
            "family_history",
        ],
        "command_standard": "The family is a mission-critical asset.",
        "doctrine": {
            "relationship_health": "core_asset",
            "communication": "preventive_maintenance",
            "legal_clarity": "asset_protection",
            "family_alignment": "mission_readiness",
        },
    }


@router.get("/status")
def family_status():
    aars = read_json(FAMILY_AARS_FILE, [])
    alignments = read_json(FAMILY_ALIGNMENTS_FILE, [])
    asset_reviews = read_json(FAMILY_ASSET_REVIEWS_FILE, [])

    return {
        "status": "ok",
        "module": "family_stability",
        "operating_mode": "preventive",
        "records": {
            "weekly_aars": len(aars),
            "household_alignments": len(alignments),
            "asset_reviews": len(asset_reviews),
        },
        "primary_risks_monitored": [
            "communication_gap",
            "resentment_build_up",
            "financial_avoidance",
            "unclear_asset_boundaries",
            "business_family_conflict",
            "schedule_misalignment",
            "unresolved_parenting_stress",
        ],
        "recommended_cadence": {
            "daily": "Detect obvious family/admin stressors.",
            "weekly": "Run marriage/family AAR.",
            "monthly": "Review household finances and asset boundaries.",
            "quarterly": "Review legal, business, estate, and insurance alignment.",
            "annually": "Run legacy and family resilience review.",
        },
        "next_action": "Run the weekly family AAR and identify one repair action.",
    }


@router.get("/history")
def family_history():
    aars = read_json(FAMILY_AARS_FILE, [])
    alignments = read_json(FAMILY_ALIGNMENTS_FILE, [])
    asset_reviews = read_json(FAMILY_ASSET_REVIEWS_FILE, [])

    return {
        "status": "ok",
        "module": "family_history",
        "counts": {
            "weekly_aars": len(aars),
            "household_alignments": len(alignments),
            "asset_reviews": len(asset_reviews),
        },
        "records": {
            "weekly_aars": aars,
            "household_alignments": alignments,
            "asset_reviews": asset_reviews,
        },
        "next_action": "Review family records for recurring stressors, unresolved topics, and missing legal or financial clarity.",
    }


@router.post("/weekly-aar")
def weekly_family_aar(payload: FamilyAARRequest):
    result = build_weekly_aar_result(payload)

    record = {
        "id": str(uuid4()),
        "created_at": now_utc(),
        "type": "weekly_family_aar",
        "result": result,
    }

    append_record(FAMILY_AARS_FILE, record)

    return {
        **result,
        "record_id": record["id"],
        "stored": True,
    }


@router.post("/conflict-repair")
def conflict_repair(payload: ConflictRepairRequest):
    escalation_risks = []

    if payload.assumptions:
        escalation_risks.append("assumptions_present")

    if not payload.facts:
        escalation_risks.append("facts_not_separated")

    if not payload.desired_repair:
        escalation_risks.append("repair_not_defined")

    return {
        "issue": payload.issue,
        "escalation_risks": escalation_risks,
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
    result = build_asset_review_result(payload)

    record = {
        "id": str(uuid4()),
        "created_at": now_utc(),
        "type": "family_asset_protection_review",
        "result": result,
    }

    append_record(FAMILY_ASSET_REVIEWS_FILE, record)

    return {
        **result,
        "record_id": record["id"],
        "stored": True,
    }


@router.post("/household-alignment")
def household_alignment(payload: HouseholdAlignmentRequest):
    result = build_household_alignment_result(payload)

    record = {
        "id": str(uuid4()),
        "created_at": now_utc(),
        "type": "household_alignment",
        "result": result,
    }

    append_record(FAMILY_ALIGNMENTS_FILE, record)

    return {
        **result,
        "record_id": record["id"],
        "stored": True,
    }


@router.post("/reset")
def family_reset(payload: FamilyResetRequest):
    if payload.confirmation != "RESET_FAMILY_STABILITY_DEV_DATA":
        raise HTTPException(status_code=400, detail="Reset confirmation required.")

    write_json(FAMILY_AARS_FILE, [])
    write_json(FAMILY_ALIGNMENTS_FILE, [])
    write_json(FAMILY_ASSET_REVIEWS_FILE, [])

    return {
        "status": "ok",
        "reset": True,
        "cleared": {
            "weekly_aars": True,
            "household_alignments": True,
            "asset_reviews": True,
        },
    }


@router.get("/dashboard", response_class=HTMLResponse)
def family_dashboard():
    html = """
    <!doctype html>
    <html>
      <head>
        <title>Project Salus — Family Stability</title>
      </head>
      <body>
        <h1>Project Salus — Family Stability</h1>
        <p>Family cohesion, communication, household alignment, and legacy protection.</p>
        <ul>
          <li><a href="/family/status">Family Status</a></li>
          <li><a href="/family/readiness">Family Readiness</a></li>
          <li><a href="/family/history">Family History</a></li>
          <li><a href="/command/home">Command Home</a></li>
        </ul>
      </body>
    </html>
    """
    return HTMLResponse(content=html)
