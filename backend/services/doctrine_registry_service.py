import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional


DATA_DIR = Path("data")
DOCTRINE_FILE = DATA_DIR / "doctrine_registry_records.json"
LESSONS_FILE = DATA_DIR / "doctrine_registry_lessons.json"

DOCTRINE_STATUSES = [
    "proposed",
    "active",
    "needs_review",
    "retired",
]

DOCTRINE_CATEGORIES = [
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

EVIDENCE_LEVELS = [
    "verified_fact",
    "strong_evidence",
    "expert_opinion",
    "emerging_theory",
    "ai_generated_pattern",
    "speculation",
    "unverified_claim",
]

DOCTRINE_REGISTRY_DOCTRINE = (
    "Project Salus must turn repeated lessons into explicit doctrine so the system becomes more disciplined "
    "after every mission, decision, AAR, and failure."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not DOCTRINE_FILE.exists():
        DOCTRINE_FILE.write_text("[]")

    if not LESSONS_FILE.exists():
        LESSONS_FILE.write_text("[]")


def read_json_list(path: Path) -> List[Dict[str, Any]]:
    ensure_store()

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    return [item for item in data if isinstance(item, dict)]


def write_json_list(path: Path, records: List[Dict[str, Any]]) -> None:
    ensure_store()
    path.write_text(json.dumps(records, indent=2, sort_keys=True))


def normalize_list(values: Any) -> List[str]:
    if not values:
        return []

    if isinstance(values, list):
        return [str(v).strip() for v in values if str(v).strip()]

    return [str(values).strip()]


def normalize_choice(value: Any, allowed: List[str], default: str) -> str:
    normalized = str(value or default).strip().lower()
    if normalized not in allowed:
        return default
    return normalized


def clamp_score(value: Any) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        return 0

    return max(0, min(score, 10))


def build_record_id(prefix: str, *parts: str) -> str:
    raw = "|".join(parts + (utc_now(),)).lower().encode("utf-8")
    digest = sha256(raw).hexdigest()[:10]
    return f"{prefix}_{digest}"


def create_doctrine_record(payload: Dict[str, Any]) -> Dict[str, Any]:
    ensure_store()

    title = payload.get("title", "Untitled Doctrine")
    statement = payload.get("statement", "")
    category = normalize_choice(payload.get("category"), DOCTRINE_CATEGORIES, "general")
    status = normalize_choice(payload.get("status"), DOCTRINE_STATUSES, "proposed")
    evidence_level = normalize_choice(payload.get("evidence_level"), EVIDENCE_LEVELS, "unverified_claim")

    doctrine = {
        "doctrine_id": build_record_id("doc", title, statement),
        "title": title,
        "statement": statement,
        "category": category,
        "status": status,
        "evidence_level": evidence_level,
        "source": payload.get("source", "manual"),
        "rationale": payload.get("rationale", ""),
        "triggers": normalize_list(payload.get("triggers")),
        "rules": normalize_list(payload.get("rules")),
        "risks_if_ignored": normalize_list(payload.get("risks_if_ignored")),
        "review_notes": normalize_list(payload.get("review_notes")),
        "confidence_score": clamp_score(payload.get("confidence_score")),
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "doctrine": DOCTRINE_REGISTRY_DOCTRINE,
    }

    records = read_json_list(DOCTRINE_FILE)
    records.append(doctrine)
    write_json_list(DOCTRINE_FILE, records)

    return {
        "saved": True,
        "doctrine": doctrine,
        "next_action": build_doctrine_next_action(doctrine),
    }


def build_doctrine_next_action(doctrine: Dict[str, Any]) -> str:
    if doctrine.get("status") == "active":
        return "Apply this doctrine in relevant modules and future decisions."

    if doctrine.get("status") == "needs_review":
        return "Review evidence, risks, and fit before applying this doctrine."

    if doctrine.get("status") == "retired":
        return "Keep archived for history only. Do not apply by default."

    return "Validate this proposed doctrine before promoting to active."


def list_doctrine(
    category: Optional[str] = None,
    status: Optional[str] = None,
    evidence_level: Optional[str] = None,
) -> Dict[str, Any]:
    records = read_json_list(DOCTRINE_FILE)
    filtered = records

    if category:
        filtered = [item for item in filtered if item.get("category") == category]

    if status:
        filtered = [item for item in filtered if item.get("status") == status]

    if evidence_level:
        filtered = [item for item in filtered if item.get("evidence_level") == evidence_level]

    filtered = sorted(
        filtered,
        key=lambda item: (item.get("status") != "active", item.get("category", ""), item.get("title", "")),
    )

    return {
        "count": len(filtered),
        "doctrine": filtered,
        "filters": {
            "category": category,
            "status": status,
            "evidence_level": evidence_level,
        },
    }


def get_doctrine(doctrine_id: str) -> Dict[str, Any]:
    records = read_json_list(DOCTRINE_FILE)

    for item in records:
        if item.get("doctrine_id") == doctrine_id:
            return {
                "found": True,
                "doctrine": item,
            }

    return {
        "found": False,
        "doctrine": None,
    }


def update_doctrine_status(payload: Dict[str, Any]) -> Dict[str, Any]:
    doctrine_id = payload.get("doctrine_id", "")
    status = normalize_choice(payload.get("status"), DOCTRINE_STATUSES, "needs_review")
    review_note = str(payload.get("review_note", "")).strip()

    records = read_json_list(DOCTRINE_FILE)
    updated = None

    for item in records:
        if item.get("doctrine_id") == doctrine_id:
            item["status"] = status
            item["updated_at"] = utc_now()

            if review_note:
                item.setdefault("review_notes", [])
                item["review_notes"].append(review_note)

            updated = item
            break

    if updated is None:
        return {
            "updated": False,
            "reason": "Doctrine not found.",
            "doctrine_id": doctrine_id,
        }

    write_json_list(DOCTRINE_FILE, records)

    return {
        "updated": True,
        "doctrine": updated,
        "next_action": build_doctrine_next_action(updated),
    }


def create_lesson_record(payload: Dict[str, Any]) -> Dict[str, Any]:
    ensure_store()

    lesson = {
        "lesson_id": build_record_id(
            "lesson",
            payload.get("title", "Untitled Lesson"),
            payload.get("lesson", ""),
        ),
        "title": payload.get("title", "Untitled Lesson"),
        "lesson": payload.get("lesson", ""),
        "source": payload.get("source", "manual"),
        "category": normalize_choice(payload.get("category"), DOCTRINE_CATEGORIES, "general"),
        "mission_id": payload.get("mission_id", ""),
        "severity": normalize_choice(
            payload.get("severity"),
            ["low", "medium", "high", "critical"],
            "medium",
        ),
        "recommended_doctrine_update": payload.get("recommended_doctrine_update", ""),
        "action_items": normalize_list(payload.get("action_items")),
        "created_at": utc_now(),
    }

    records = read_json_list(LESSONS_FILE)
    records.append(lesson)
    write_json_list(LESSONS_FILE, records)

    doctrine_candidate = None

    if lesson["recommended_doctrine_update"]:
        doctrine_candidate = {
            "title": f"Doctrine candidate from lesson: {lesson['title']}",
            "statement": lesson["recommended_doctrine_update"],
            "category": lesson["category"],
            "status": "proposed",
            "evidence_level": "expert_opinion",
            "source": lesson["source"],
            "rationale": lesson["lesson"],
            "triggers": ["lesson_learned", lesson["severity"]],
            "rules": [lesson["recommended_doctrine_update"]],
            "risks_if_ignored": ["Repeated failure or preventable drift."],
            "confidence_score": 6,
        }

    return {
        "saved": True,
        "lesson": lesson,
        "doctrine_candidate": doctrine_candidate,
        "next_action": (
            "Review doctrine candidate and promote if it should become an operating rule."
            if doctrine_candidate
            else "Review lesson and decide whether it should create doctrine."
        ),
    }


def list_lessons(category: Optional[str] = None, severity: Optional[str] = None) -> Dict[str, Any]:
    records = read_json_list(LESSONS_FILE)
    filtered = records

    if category:
        filtered = [item for item in filtered if item.get("category") == category]

    if severity:
        filtered = [item for item in filtered if item.get("severity") == severity]

    filtered = sorted(filtered, key=lambda item: item.get("created_at", ""), reverse=True)

    return {
        "count": len(filtered),
        "lessons": filtered,
        "filters": {
            "category": category,
            "severity": severity,
        },
    }


def build_doctrine_dashboard() -> Dict[str, Any]:
    doctrine_records = read_json_list(DOCTRINE_FILE)
    lesson_records = read_json_list(LESSONS_FILE)

    status_counts = {status: 0 for status in DOCTRINE_STATUSES}
    category_counts = {category: 0 for category in DOCTRINE_CATEGORIES}
    evidence_counts = {level: 0 for level in EVIDENCE_LEVELS}

    review_needed: List[Dict[str, Any]] = []
    active_doctrine: List[Dict[str, Any]] = []

    for item in doctrine_records:
        status = item.get("status", "proposed")
        category = item.get("category", "general")
        evidence_level = item.get("evidence_level", "unverified_claim")

        if status in status_counts:
            status_counts[status] += 1

        if category in category_counts:
            category_counts[category] += 1

        if evidence_level in evidence_counts:
            evidence_counts[evidence_level] += 1

        if status in {"proposed", "needs_review"}:
            review_needed.append(item)

        if status == "active":
            active_doctrine.append(item)

    risk_flags: List[str] = []

    if review_needed:
        risk_flags.append("Proposed or review-needed doctrine requires command review.")

    weak_evidence_count = evidence_counts["speculation"] + evidence_counts["unverified_claim"] + evidence_counts["ai_generated_pattern"]
    if weak_evidence_count:
        risk_flags.append("Some doctrine has weak evidence and should not be treated as authority.")

    if lesson_records and not doctrine_records:
        risk_flags.append("Lessons exist but have not been converted into doctrine.")

    return {
        "module": "doctrine_registry_dashboard",
        "total_doctrine": len(doctrine_records),
        "total_lessons": len(lesson_records),
        "status_counts": status_counts,
        "category_counts": category_counts,
        "evidence_counts": evidence_counts,
        "review_needed": review_needed,
        "active_doctrine": active_doctrine,
        "risk_flags": risk_flags,
        "next_action": (
            "Review proposed doctrine and promote, revise, or retire."
            if review_needed
            else "Continue capturing lessons and doctrine updates after missions."
        ),
        "doctrine": DOCTRINE_REGISTRY_DOCTRINE,
    }


def reset_registry() -> Dict[str, Any]:
    write_json_list(DOCTRINE_FILE, [])
    write_json_list(LESSONS_FILE, [])

    return {
        "reset": True,
        "doctrine": 0,
        "lessons": 0,
    }
