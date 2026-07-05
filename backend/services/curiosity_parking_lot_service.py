import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional


DATA_DIR = Path("data")
PARKING_FILE = DATA_DIR / "curiosity_parking_lot_items.json"

PARKING_STATUSES = [
    "parked",
    "reviewing",
    "promoted_to_mission",
    "promoted_to_doctrine",
    "discarded",
    "archived",
]

REVIEW_CADENCES = ["daily", "weekly", "monthly", "quarterly", "none"]

PARKING_DOCTRINE = (
    "Curiosity is not opportunity. Park low-certainty or low-priority ideas until evidence, "
    "strategic fit, or actionability justify promotion."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not PARKING_FILE.exists():
        PARKING_FILE.write_text("[]")


def read_items() -> List[Dict[str, Any]]:
    ensure_store()
    try:
        data = json.loads(PARKING_FILE.read_text())
    except json.JSONDecodeError:
        return []
    return [item for item in data if isinstance(item, dict)] if isinstance(data, list) else []


def write_items(items: List[Dict[str, Any]]) -> None:
    ensure_store()
    PARKING_FILE.write_text(json.dumps(items, indent=2, sort_keys=True))


def normalize_list(values: Any) -> List[str]:
    if not values:
        return []
    if isinstance(values, list):
        return [str(v).strip() for v in values if str(v).strip()]
    return [str(values).strip()]


def clamp_score(value: Any) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(score, 10))


def normalize_choice(value: Any, allowed: List[str], default: str) -> str:
    normalized = str(value or default).strip().lower()
    return normalized if normalized in allowed else default


def build_item_id(title: str, summary: str) -> str:
    raw = f"{title}|{summary}|{utc_now()}".lower().encode("utf-8")
    return f"park_{sha256(raw).hexdigest()[:10]}"


def calculate_reconsideration_score(payload: Dict[str, Any]) -> int:
    weighted = (
        clamp_score(payload.get("strategic_fit")) * 0.25
        + clamp_score(payload.get("evidence_strength")) * 0.20
        + clamp_score(payload.get("actionability")) * 0.20
        + clamp_score(payload.get("roi")) * 0.15
        + clamp_score(payload.get("urgency")) * 0.08
        + (10 - clamp_score(payload.get("risk"))) * 0.07
        + (10 - clamp_score(payload.get("opportunity_cost"))) * 0.05
    )
    return round(weighted * 10)


def classify_reconsideration(score: int) -> str:
    if score >= 75:
        return "promote_candidate"
    if score >= 50:
        return "review_later"
    if score >= 30:
        return "keep_parked"
    return "discard_candidate"


def park_item(payload: Dict[str, Any]) -> Dict[str, Any]:
    score = calculate_reconsideration_score(payload)
    item = {
        "item_id": build_item_id(payload.get("title", "Untitled Parked Item"), payload.get("summary", "")),
        "title": payload.get("title", "Untitled Parked Item"),
        "summary": payload.get("summary", ""),
        "source": payload.get("source", "manual"),
        "source_type": payload.get("source_type", "other"),
        "topics": normalize_list(payload.get("topics")),
        "claims": normalize_list(payload.get("claims")),
        "reason_parked": payload.get("reason_parked", ""),
        "status": normalize_choice(payload.get("status"), PARKING_STATUSES, "parked"),
        "review_cadence": normalize_choice(payload.get("review_cadence"), REVIEW_CADENCES, "weekly"),
        "strategic_fit": clamp_score(payload.get("strategic_fit")),
        "evidence_strength": clamp_score(payload.get("evidence_strength")),
        "actionability": clamp_score(payload.get("actionability")),
        "roi": clamp_score(payload.get("roi")),
        "urgency": clamp_score(payload.get("urgency")),
        "risk": clamp_score(payload.get("risk")),
        "opportunity_cost": clamp_score(payload.get("opportunity_cost")),
        "reconsideration_score": score,
        "reconsideration_class": classify_reconsideration(score),
        "verification_needed": normalize_list(payload.get("verification_needed")),
        "promotion_path": payload.get("promotion_path", "undecided"),
        "review_notes": normalize_list(payload.get("review_notes")),
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "doctrine": PARKING_DOCTRINE,
    }

    items = read_items()
    items.append(item)
    write_items(items)

    return {"saved": True, "item": item, "next_action": build_next_action(item)}


def build_next_action(item: Dict[str, Any]) -> str:
    if item["reconsideration_class"] == "promote_candidate":
        return "Review for promotion to mission or doctrine candidate."
    if item["reconsideration_class"] == "discard_candidate":
        return "Consider discard unless new evidence appears."
    return "Keep parked. Do not interrupt active missions."


def list_items(status: Optional[str] = None, topic: Optional[str] = None, review_cadence: Optional[str] = None) -> Dict[str, Any]:
    items = read_items()

    if status:
        items = [item for item in items if item.get("status") == status]
    if topic:
        items = [item for item in items if topic.lower() in [t.lower() for t in item.get("topics", [])]]
    if review_cadence:
        items = [item for item in items if item.get("review_cadence") == review_cadence]

    items = sorted(items, key=lambda item: item.get("reconsideration_score", 0), reverse=True)
    return {"count": len(items), "items": items}


def get_item(item_id: str) -> Dict[str, Any]:
    for item in read_items():
        if item.get("item_id") == item_id:
            return {"found": True, "item": item}
    return {"found": False, "item": None}


def update_item_status(payload: Dict[str, Any]) -> Dict[str, Any]:
    items = read_items()
    item_id = payload.get("item_id", "")
    status = normalize_choice(payload.get("status"), PARKING_STATUSES, "reviewing")
    updated = None

    for item in items:
        if item.get("item_id") == item_id:
            item["status"] = status
            item["updated_at"] = utc_now()
            note = str(payload.get("review_note", "")).strip()
            if note:
                item.setdefault("review_notes", []).append(note)
            updated = item
            break

    if not updated:
        return {"updated": False, "reason": "Parking lot item not found.", "item_id": item_id}

    write_items(items)
    return {"updated": True, "item": updated, "next_action": "Review status and act accordingly."}


def review_item(payload: Dict[str, Any]) -> Dict[str, Any]:
    items = read_items()
    item_id = payload.get("item_id", "")
    reviewed = None

    for item in items:
        if item.get("item_id") == item_id:
            item["evidence_strength"] = clamp_score(payload.get("evidence_strength"))
            item["actionability"] = clamp_score(payload.get("actionability"))
            item["strategic_fit"] = clamp_score(payload.get("strategic_fit"))
            item["roi"] = clamp_score(payload.get("roi"))
            item["reconsideration_score"] = calculate_reconsideration_score(item)
            item["reconsideration_class"] = classify_reconsideration(item["reconsideration_score"])
            item["updated_at"] = utc_now()

            path = str(payload.get("recommended_path", "keep_parked")).lower()
            if path == "mission":
                item["status"] = "promoted_to_mission"
            elif path == "doctrine":
                item["status"] = "promoted_to_doctrine"
            elif path == "discard":
                item["status"] = "discarded"
            elif path == "archive":
                item["status"] = "archived"
            else:
                item["status"] = "parked"

            note = str(payload.get("review_note", "")).strip()
            if note:
                item.setdefault("review_notes", []).append(note)

            reviewed = item
            break

    if not reviewed:
        return {"reviewed": False, "reason": "Parking lot item not found.", "item_id": item_id}

    write_items(items)
    return {
        "reviewed": True,
        "item": reviewed,
        "mission_candidate": build_mission_candidate(reviewed),
        "doctrine_candidate": build_doctrine_candidate(reviewed),
        "next_action": "Create corresponding mission/doctrine record if promoted.",
    }


def build_mission_candidate(item: Dict[str, Any]) -> Dict[str, Any]:
    if item.get("status") != "promoted_to_mission":
        return {}
    return {
        "title": f"Validate parked item: {item.get('title', 'Untitled')}",
        "objective": item.get("summary", "Validate parked item."),
        "source": "curiosity_parking_lot",
        "owner": "Kyle",
        "status": "planned",
        "strategic_fit": item.get("strategic_fit", 5),
        "roi": item.get("roi", 5),
        "urgency": item.get("urgency", 5),
        "risk": item.get("risk", 5),
        "difficulty": 5,
        "opportunity_cost": item.get("opportunity_cost", 5),
        "success_criteria": ["Claim verified, rejected, or scoped."],
        "next_actions": ["Verify the strongest claim or test the smallest version."],
    }


def build_doctrine_candidate(item: Dict[str, Any]) -> Dict[str, Any]:
    if item.get("status") != "promoted_to_doctrine":
        return {}
    statement = item.get("claims", [item.get("summary", "")])[0] if item.get("claims") else item.get("summary", "")
    return {
        "title": f"Doctrine candidate from parked item: {item.get('title', 'Untitled')}",
        "statement": statement,
        "category": "strategy",
        "status": "proposed",
        "evidence_level": "expert_opinion" if item.get("evidence_strength", 0) >= 6 else "unverified_claim",
        "source": "curiosity_parking_lot",
        "rationale": item.get("summary", ""),
        "triggers": ["parking_lot_review"],
        "rules": [statement] if statement else [],
        "risks_if_ignored": ["Potentially useful lesson may be lost."],
        "confidence_score": min(8, item.get("evidence_strength", 5)),
    }


def build_dashboard() -> Dict[str, Any]:
    items = read_items()
    promote = [i for i in items if i.get("reconsideration_class") == "promote_candidate"]
    discard = [i for i in items if i.get("reconsideration_class") == "discard_candidate"]

    status_counts = {s: 0 for s in PARKING_STATUSES}
    for item in items:
        if item.get("status") in status_counts:
            status_counts[item["status"]] += 1

    risk_flags = []
    if promote:
        risk_flags.append("Some parked items may now justify promotion.")
    if discard:
        risk_flags.append("Some parked items should be discarded or archived.")

    return {
        "module": "curiosity_parking_lot_dashboard",
        "total_items": len(items),
        "status_counts": status_counts,
        "promote_candidates": promote[:5],
        "discard_candidates": discard[:5],
        "risk_flags": risk_flags,
        "next_action": "Review promote candidates first." if promote else "Review and discard low-signal items on schedule.",
        "doctrine": PARKING_DOCTRINE,
    }


def reset_parking_lot() -> Dict[str, Any]:
    write_items([])
    return {"reset": True, "items": 0}
