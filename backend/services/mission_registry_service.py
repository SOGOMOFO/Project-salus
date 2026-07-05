import json
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, List, Optional


DATA_DIR = Path("data")
MISSIONS_FILE = DATA_DIR / "mission_registry_missions.json"
AARS_FILE = DATA_DIR / "mission_registry_aars.json"

MISSION_STATUSES = [
    "planned",
    "active",
    "blocked",
    "completed",
    "paused",
    "cancelled",
]

MISSION_REGISTRY_DOCTRINE = (
    "Execution requires memory. Mission history, status, blockers, AARs, and lessons learned "
    "must persist so Salus improves over time."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_store() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not MISSIONS_FILE.exists():
        MISSIONS_FILE.write_text("[]")

    if not AARS_FILE.exists():
        AARS_FILE.write_text("[]")


def read_json_list(path: Path) -> List[Dict[str, Any]]:
    ensure_store()

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        data = []

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


def clamp_score(value: Any) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        return 0

    return max(0, min(score, 10))


def build_mission_id(title: str, objective: str) -> str:
    raw = f"{title}|{objective}|{utc_now()}".lower().encode("utf-8")
    digest = sha256(raw).hexdigest()[:10]
    return f"mission_{digest}"


def priority_level(score: int) -> str:
    if score >= 80:
        return "critical"
    if score >= 65:
        return "high"
    if score >= 45:
        return "medium"
    return "low"


def calculate_priority_score(payload: Dict[str, Any]) -> int:
    strategic_fit = clamp_score(payload.get("strategic_fit"))
    roi = clamp_score(payload.get("roi"))
    urgency = clamp_score(payload.get("urgency"))
    risk = clamp_score(payload.get("risk"))
    difficulty = clamp_score(payload.get("difficulty"))
    opportunity_cost = clamp_score(payload.get("opportunity_cost"))

    weighted = (
        strategic_fit * 0.25
        + roi * 0.20
        + urgency * 0.20
        + (10 - risk) * 0.12
        + (10 - difficulty) * 0.10
        + (10 - opportunity_cost) * 0.08
        + 5 * 0.05
    )

    return round(weighted * 10)


def create_registry_mission(payload: Dict[str, Any]) -> Dict[str, Any]:
    ensure_store()

    title = payload.get("title", "Untitled Mission")
    objective = payload.get("objective", "")
    status = str(payload.get("status", "planned")).lower()

    if status not in MISSION_STATUSES:
        status = "planned"

    priority_score = calculate_priority_score(payload)
    mission = {
        "mission_id": build_mission_id(title, objective),
        "title": title,
        "objective": objective,
        "source": payload.get("source", "manual"),
        "owner": payload.get("owner", ""),
        "status": status,
        "deadline": payload.get("deadline", ""),
        "priority_score": priority_score,
        "priority_level": priority_level(priority_score),
        "strategic_fit": clamp_score(payload.get("strategic_fit")),
        "roi": clamp_score(payload.get("roi")),
        "urgency": clamp_score(payload.get("urgency")),
        "risk": clamp_score(payload.get("risk")),
        "difficulty": clamp_score(payload.get("difficulty")),
        "opportunity_cost": clamp_score(payload.get("opportunity_cost")),
        "success_criteria": normalize_list(payload.get("success_criteria")),
        "blockers": normalize_list(payload.get("blockers")),
        "dependencies": normalize_list(payload.get("dependencies")),
        "next_actions": normalize_list(payload.get("next_actions")),
        "progress_notes": [],
        "created_at": utc_now(),
        "updated_at": utc_now(),
        "completed_at": None,
        "doctrine": MISSION_REGISTRY_DOCTRINE,
    }

    records = read_json_list(MISSIONS_FILE)
    records.append(mission)
    write_json_list(MISSIONS_FILE, records)

    return {
        "saved": True,
        "mission": mission,
        "next_action": "Mission saved to registry. Execute, update status, and capture AAR when complete.",
    }


def list_missions(
    status: Optional[str] = None,
    owner: Optional[str] = None,
    priority: Optional[str] = None,
) -> Dict[str, Any]:
    records = read_json_list(MISSIONS_FILE)

    filtered = records

    if status:
        filtered = [item for item in filtered if item.get("status") == status]

    if owner:
        filtered = [item for item in filtered if str(item.get("owner", "")).lower() == owner.lower()]

    if priority:
        filtered = [item for item in filtered if item.get("priority_level") == priority]

    filtered = sorted(filtered, key=lambda item: item.get("priority_score", 0), reverse=True)

    return {
        "count": len(filtered),
        "missions": filtered,
        "filters": {
            "status": status,
            "owner": owner,
            "priority": priority,
        },
    }


def get_mission(mission_id: str) -> Dict[str, Any]:
    records = read_json_list(MISSIONS_FILE)
    aars = read_json_list(AARS_FILE)

    for mission in records:
        if mission.get("mission_id") == mission_id:
            mission_aars = [aar for aar in aars if aar.get("mission_id") == mission_id]
            return {
                "found": True,
                "mission": mission,
                "aars": mission_aars,
                "aar_count": len(mission_aars),
            }

    return {
        "found": False,
        "mission": None,
        "aars": [],
        "aar_count": 0,
    }


def update_registry_status(payload: Dict[str, Any]) -> Dict[str, Any]:
    ensure_store()

    mission_id = payload.get("mission_id", "")
    new_status = str(payload.get("status", "planned")).lower()

    if new_status not in MISSION_STATUSES:
        new_status = "planned"

    progress_notes = normalize_list(payload.get("progress_notes"))
    blockers = normalize_list(payload.get("blockers"))
    completed_criteria = normalize_list(payload.get("completed_criteria"))

    records = read_json_list(MISSIONS_FILE)
    updated = None

    for mission in records:
        if mission.get("mission_id") == mission_id:
            mission["status"] = new_status
            mission["updated_at"] = utc_now()

            if progress_notes:
                mission.setdefault("progress_notes", [])
                mission["progress_notes"].extend(progress_notes)

            if blockers is not None:
                mission["blockers"] = blockers

            if completed_criteria:
                mission["completed_criteria"] = completed_criteria

            if new_status == "completed":
                mission["completed_at"] = utc_now()

            updated = mission
            break

    if updated is None:
        return {
            "updated": False,
            "reason": "Mission not found.",
            "mission_id": mission_id,
        }

    write_json_list(MISSIONS_FILE, records)

    return {
        "updated": True,
        "mission": updated,
        "next_action": build_status_next_action(updated),
    }


def build_status_next_action(mission: Dict[str, Any]) -> str:
    status = mission.get("status")

    if status == "completed":
        return "Run AAR and capture lessons learned."

    if status == "blocked":
        return "Resolve or escalate blockers."

    if status == "active":
        return "Continue execution and update after next work block."

    if status == "paused":
        return "Define restart condition."

    if status == "cancelled":
        return "Archive mission and preserve cancellation reason."

    return "Schedule or activate mission."


def add_registry_aar(payload: Dict[str, Any]) -> Dict[str, Any]:
    ensure_store()

    mission_id = payload.get("mission_id", "")
    mission_result = get_mission(mission_id)

    if not mission_result["found"]:
        return {
            "saved": False,
            "reason": "Mission not found.",
            "mission_id": mission_id,
        }

    effectiveness_score = clamp_score(payload.get("effectiveness_score"))

    if effectiveness_score >= 8:
        result = "effective"
    elif effectiveness_score >= 5:
        result = "mixed"
    else:
        result = "ineffective"

    aar = {
        "aar_id": f"aar_{sha256((mission_id + utc_now()).encode('utf-8')).hexdigest()[:10]}",
        "mission_id": mission_id,
        "title": payload.get("title", mission_result["mission"].get("title", "Untitled Mission")),
        "result": result,
        "effectiveness_score": effectiveness_score,
        "what_went_well": normalize_list(payload.get("what_went_well")),
        "what_failed": normalize_list(payload.get("what_failed")),
        "lessons_learned": normalize_list(payload.get("lessons_learned")),
        "next_actions": normalize_list(payload.get("next_actions")),
        "doctrine_updates": normalize_list(payload.get("doctrine_updates")),
        "created_at": utc_now(),
    }

    aars = read_json_list(AARS_FILE)
    aars.append(aar)
    write_json_list(AARS_FILE, aars)

    return {
        "saved": True,
        "aar": aar,
        "next_action": "Feed AAR lessons into future planning, doctrine, and sprint selection.",
    }


def build_registry_dashboard() -> Dict[str, Any]:
    missions = read_json_list(MISSIONS_FILE)
    aars = read_json_list(AARS_FILE)

    status_counts = {status: 0 for status in MISSION_STATUSES}
    priority_counts = {
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
    }

    blocked_missions: List[Dict[str, Any]] = []
    active_missions: List[Dict[str, Any]] = []
    completed_missions: List[Dict[str, Any]] = []

    for mission in missions:
        status = mission.get("status", "planned")
        priority = mission.get("priority_level", "low")

        if status in status_counts:
            status_counts[status] += 1

        if priority in priority_counts:
            priority_counts[priority] += 1

        if status == "blocked":
            blocked_missions.append(mission)

        if status == "active":
            active_missions.append(mission)

        if status == "completed":
            completed_missions.append(mission)

    top_priority = sorted(
        [mission for mission in missions if mission.get("status") not in {"completed", "cancelled"}],
        key=lambda item: item.get("priority_score", 0),
        reverse=True,
    )[:5]

    risk_flags: List[str] = []

    if blocked_missions:
        risk_flags.append("Blocked missions require command attention.")

    if len(active_missions) > 5:
        risk_flags.append("Too many active missions may dilute focus.")

    if completed_missions and not aars:
        risk_flags.append("Completed missions exist without AARs.")

    return {
        "module": "mission_registry_dashboard",
        "total_missions": len(missions),
        "total_aars": len(aars),
        "status_counts": status_counts,
        "priority_counts": priority_counts,
        "top_priority_missions": top_priority,
        "blocked_missions": blocked_missions,
        "risk_flags": risk_flags,
        "next_action": (
            "Unblock blocked missions first."
            if blocked_missions
            else "Execute the highest-priority active or planned mission."
        ),
        "doctrine": MISSION_REGISTRY_DOCTRINE,
    }


def reset_registry() -> Dict[str, Any]:
    write_json_list(MISSIONS_FILE, [])
    write_json_list(AARS_FILE, [])

    return {
        "reset": True,
        "missions": 0,
        "aars": 0,
    }
