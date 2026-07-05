import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List

from backend.services.curiosity_parking_lot_service import park_item
from backend.services.doctrine_registry_service import create_doctrine_record
from backend.services.intelligence_intake_service import triage_intelligence
from backend.services.mission_registry_service import create_registry_mission


DATA_DIR = Path("data")
WORKFLOW_RUNS_FILE = DATA_DIR / "workflow_orchestrator_runs.json"

WORKFLOW_TYPES = [
    "intelligence_to_action",
    "mission_candidate_create",
    "doctrine_candidate_create",
]

WORKFLOW_ACTIONS = [
    "triaged",
    "parked",
    "mission_created",
    "doctrine_created",
    "discarded",
    "manual_review_required",
]

WORKFLOW_DOCTRINE = (
    "Project Salus should not leave useful intelligence stranded. Intake must either become a mission, "
    "doctrine candidate, verification task, parked item, or discarded record."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not WORKFLOW_RUNS_FILE.exists():
        WORKFLOW_RUNS_FILE.write_text("[]")


def read_runs() -> List[Dict[str, Any]]:
    ensure_store()
    try:
        data = json.loads(WORKFLOW_RUNS_FILE.read_text())
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    return [item for item in data if isinstance(item, dict)]


def write_runs(records: List[Dict[str, Any]]) -> None:
    ensure_store()
    WORKFLOW_RUNS_FILE.write_text(json.dumps(records, indent=2, sort_keys=True))


def clamp_score(value: Any) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(score, 10))


def build_run_id(title: str, workflow_type: str) -> str:
    raw = f"{title}|{workflow_type}|{utc_now()}".lower().encode("utf-8")
    return f"workflow_{sha256(raw).hexdigest()[:10]}"


def evidence_strength_from_level(evidence_level: str) -> int:
    mapping = {
        "verified_fact": 10,
        "strong_evidence": 9,
        "expert_opinion": 7,
        "emerging_theory": 5,
        "ai_generated_pattern": 3,
        "speculation": 2,
        "unverified_claim": 1,
    }
    return mapping.get(str(evidence_level or "unverified_claim").lower(), 1)


def save_workflow_run(run: Dict[str, Any]) -> Dict[str, Any]:
    records = read_runs()
    records.append(run)
    write_runs(records)
    return run


def build_parking_payload(item: Dict[str, Any], triage: Dict[str, Any], reason: str) -> Dict[str, Any]:
    return {
        "title": item.get("title", triage.get("title", "Untitled Intelligence Item")),
        "summary": item.get("summary", ""),
        "source": "workflow_orchestrator",
        "source_type": item.get("source_type", "other"),
        "topics": triage.get("topics", item.get("topics", [])),
        "claims": triage.get("claims", item.get("claims", [])),
        "reason_parked": reason,
        "status": "parked",
        "review_cadence": "weekly",
        "strategic_fit": clamp_score(item.get("strategic_fit", 5)),
        "evidence_strength": evidence_strength_from_level(triage.get("evidence_level")),
        "actionability": clamp_score(item.get("actionability", 5)),
        "roi": clamp_score(item.get("roi", 5)),
        "urgency": clamp_score(item.get("urgency", 5)),
        "risk": clamp_score(item.get("risk", 5)),
        "opportunity_cost": clamp_score(item.get("opportunity_cost", 5)),
        "verification_needed": triage.get("verification_plan", []),
        "promotion_path": "undecided",
        "review_notes": [
            "Created by Workflow Orchestrator after Intelligence Intake triage."
        ],
    }


def build_mission_payload(candidate: Dict[str, Any], item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": candidate.get("title", f"Validate intelligence item: {item.get('title', 'Untitled')}"),
        "objective": candidate.get("objective", "Validate high-signal intelligence and determine action."),
        "source": candidate.get("source", "workflow_orchestrator"),
        "owner": candidate.get("owner", item.get("owner", "Kyle")),
        "status": candidate.get("status", "planned"),
        "deadline": candidate.get("deadline", ""),
        "strategic_fit": clamp_score(candidate.get("strategic_fit", item.get("strategic_fit", 5))),
        "roi": clamp_score(candidate.get("roi", item.get("roi", 5))),
        "urgency": clamp_score(candidate.get("urgency", item.get("urgency", 5))),
        "risk": clamp_score(candidate.get("risk", item.get("risk", 5))),
        "difficulty": clamp_score(candidate.get("difficulty", item.get("difficulty", 5))),
        "opportunity_cost": clamp_score(candidate.get("opportunity_cost", item.get("opportunity_cost", 5))),
        "success_criteria": candidate.get(
            "success_criteria",
            ["Top claim verified or rejected.", "One practical next action identified."],
        ),
        "blockers": candidate.get("blockers", []),
        "dependencies": candidate.get("dependencies", []),
        "next_actions": candidate.get("next_actions", ["Verify the central claim."]),
    }


def build_doctrine_payload(candidate: Dict[str, Any], item: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "title": candidate.get("title", f"Doctrine candidate: {item.get('title', 'Untitled')}"),
        "statement": candidate.get("statement", item.get("summary", "Review doctrine candidate.")),
        "category": candidate.get("category", "general"),
        "status": candidate.get("status", "proposed"),
        "evidence_level": candidate.get("evidence_level", item.get("evidence_level", "unverified_claim")),
        "source": candidate.get("source", "workflow_orchestrator"),
        "rationale": candidate.get("rationale", item.get("summary", "")),
        "triggers": candidate.get("triggers", ["workflow_orchestrator"]),
        "rules": candidate.get("rules", []),
        "risks_if_ignored": candidate.get("risks_if_ignored", ["Useful lesson may not be retained."]),
        "review_notes": candidate.get("review_notes", []),
        "confidence_score": clamp_score(candidate.get("confidence_score", item.get("source_trust", 5))),
    }


def run_intelligence_workflow(payload: Dict[str, Any]) -> Dict[str, Any]:
    item = payload.get("item", {})
    if not isinstance(item, dict):
        item = {}

    auto_create_records = bool(payload.get("auto_create_records", True))
    park_verify_items = bool(payload.get("park_verify_items", True))
    create_discard_records = bool(payload.get("create_discard_records", False))

    triage = triage_intelligence(item)
    recommendation = triage.get("triage", {}).get("recommendation", "PARK")
    route = triage.get("triage", {}).get("recommended_route", "curiosity_parking_lot")

    actions_taken: List[str] = ["triaged"]
    created_records: Dict[str, Any] = {}
    warnings: List[str] = []

    if auto_create_records:
        if recommendation == "CONVERT_TO_MISSION":
            mission_payload = build_mission_payload(triage.get("mission_candidate", {}), item)
            mission_result = create_registry_mission(mission_payload)
            created_records["mission"] = mission_result.get("mission")
            actions_taken.append("mission_created")

        elif recommendation == "CONVERT_TO_DOCTRINE_CANDIDATE":
            doctrine_payload = build_doctrine_payload(triage.get("doctrine_candidate", {}), item)
            doctrine_result = create_doctrine_record(doctrine_payload)
            created_records["doctrine"] = doctrine_result.get("doctrine")
            actions_taken.append("doctrine_created")

        elif recommendation in {"VERIFY_FIRST", "PARK"} and park_verify_items:
            reason = (
                "Requires verification before operational use."
                if recommendation == "VERIFY_FIRST"
                else "Parked for later review."
            )
            parking_result = park_item(build_parking_payload(item, triage, reason))
            created_records["parking_lot_item"] = parking_result.get("item")
            actions_taken.append("parked")

        elif recommendation == "DISCARD":
            actions_taken.append("discarded")
            if create_discard_records:
                parking_payload = build_parking_payload(
                    item,
                    triage,
                    "Discarded by triage but saved for historical reference.",
                )
                parking_payload["status"] = "discarded"
                parking_result = park_item(parking_payload)
                created_records["parking_lot_item"] = parking_result.get("item")
                actions_taken.append("parked")
    else:
        warnings.append("Auto-create disabled; review triage output manually.")
        actions_taken.append("manual_review_required")

    run = {
        "run_id": build_run_id(item.get("title", "Untitled Intelligence Item"), "intelligence_to_action"),
        "workflow_type": "intelligence_to_action",
        "input_title": item.get("title", "Untitled Intelligence Item"),
        "triage_recommendation": recommendation,
        "triage_route": route,
        "actions_taken": actions_taken,
        "created_records": created_records,
        "warnings": warnings,
        "triage": triage,
        "created_at": utc_now(),
        "doctrine": WORKFLOW_DOCTRINE,
        "next_action": build_next_action(recommendation, created_records, warnings),
    }

    return save_workflow_run(run)


def build_next_action(recommendation: str, created_records: Dict[str, Any], warnings: List[str]) -> str:
    if warnings:
        return "Review triage output manually before creating records."

    if "mission" in created_records:
        return "Review created mission in Mission Registry and execute when ready."

    if "doctrine" in created_records:
        return "Review created doctrine candidate and promote, revise, or retire."

    if "parking_lot_item" in created_records:
        return "Review parked item at the assigned cadence or after new evidence appears."

    if recommendation == "DISCARD":
        return "No execution required. Return to active missions."

    return "Review workflow output and choose mission, doctrine, parking lot, or discard."


def create_mission_from_candidate(payload: Dict[str, Any]) -> Dict[str, Any]:
    candidate = payload.get("mission_candidate", {})
    source_item = payload.get("source_item", {})

    if not isinstance(candidate, dict):
        candidate = {}
    if not isinstance(source_item, dict):
        source_item = {}

    mission_payload = build_mission_payload(candidate, source_item)
    mission_result = create_registry_mission(mission_payload)

    run = {
        "run_id": build_run_id(mission_payload.get("title", "Untitled Mission"), "mission_candidate_create"),
        "workflow_type": "mission_candidate_create",
        "actions_taken": ["mission_created"],
        "created_records": {"mission": mission_result.get("mission")},
        "created_at": utc_now(),
        "doctrine": WORKFLOW_DOCTRINE,
        "next_action": "Review created mission and execute when ready.",
    }

    return save_workflow_run(run)


def create_doctrine_from_candidate(payload: Dict[str, Any]) -> Dict[str, Any]:
    candidate = payload.get("doctrine_candidate", {})
    source_item = payload.get("source_item", {})

    if not isinstance(candidate, dict):
        candidate = {}
    if not isinstance(source_item, dict):
        source_item = {}

    doctrine_payload = build_doctrine_payload(candidate, source_item)
    doctrine_result = create_doctrine_record(doctrine_payload)

    run = {
        "run_id": build_run_id(doctrine_payload.get("title", "Untitled Doctrine"), "doctrine_candidate_create"),
        "workflow_type": "doctrine_candidate_create",
        "actions_taken": ["doctrine_created"],
        "created_records": {"doctrine": doctrine_result.get("doctrine")},
        "created_at": utc_now(),
        "doctrine": WORKFLOW_DOCTRINE,
        "next_action": "Review created doctrine candidate and promote, revise, or retire.",
    }

    return save_workflow_run(run)


def list_workflow_runs() -> Dict[str, Any]:
    runs = sorted(read_runs(), key=lambda item: item.get("created_at", ""), reverse=True)
    action_counts = {action: 0 for action in WORKFLOW_ACTIONS}

    for run in runs:
        for action in run.get("actions_taken", []):
            if action in action_counts:
                action_counts[action] += 1

    return {
        "count": len(runs),
        "runs": runs,
        "action_counts": action_counts,
    }


def build_workflow_dashboard() -> Dict[str, Any]:
    runs = read_runs()
    action_counts = {action: 0 for action in WORKFLOW_ACTIONS}
    recommendation_counts: Dict[str, int] = {}

    for run in runs:
        recommendation = run.get("triage_recommendation", "unknown")
        recommendation_counts[recommendation] = recommendation_counts.get(recommendation, 0) + 1

        for action in run.get("actions_taken", []):
            if action in action_counts:
                action_counts[action] += 1

    risk_flags: List[str] = []

    if action_counts["manual_review_required"] > 0:
        risk_flags.append("Some workflow runs require manual review.")

    if action_counts["parked"] > action_counts["mission_created"] + action_counts["doctrine_created"] + 10:
        risk_flags.append("Parking lot may be accumulating faster than execution outputs.")

    if not runs:
        risk_flags.append("No workflow runs recorded yet.")

    return {
        "module": "workflow_orchestrator_dashboard",
        "total_runs": len(runs),
        "action_counts": action_counts,
        "recommendation_counts": recommendation_counts,
        "risk_flags": risk_flags,
        "next_action": "Run an intelligence workflow on the next incoming high-signal item."
        if not runs
        else "Review parked items and execute mission outputs.",
        "doctrine": WORKFLOW_DOCTRINE,
    }


def reset_workflows() -> Dict[str, Any]:
    write_runs([])
    return {
        "reset": True,
        "workflow_runs": 0,
    }
