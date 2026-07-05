from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict, List


MISSION_STATUSES = [
    "planned",
    "active",
    "blocked",
    "completed",
    "paused",
    "cancelled",
]

MISSION_RECOMMENDATIONS = [
    "EXECUTE_NOW",
    "SCHEDULE",
    "UNBLOCK_FIRST",
    "PAUSE",
    "CANCEL",
]

MISSION_DOCTRINE = (
    "A recommendation is not progress until it becomes a tracked mission with an owner, "
    "success criteria, blockers, status, and an AAR loop."
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


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
    raw = f"{title}|{objective}".lower().encode("utf-8")
    digest = sha256(raw).hexdigest()[:10]
    return f"mission_{digest}"


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


def classify_priority(score: int) -> str:
    if score >= 80:
        return "critical"
    if score >= 65:
        return "high"
    if score >= 45:
        return "medium"
    return "low"


def detect_execution_gaps(payload: Dict[str, Any]) -> List[str]:
    gaps: List[str] = []

    owner = str(payload.get("owner", "")).strip()
    success_criteria = normalize_list(payload.get("success_criteria"))
    blockers = normalize_list(payload.get("blockers"))
    objective = str(payload.get("objective", "")).strip()

    if not objective:
        gaps.append("objective_missing")

    if not owner:
        gaps.append("owner_missing")

    if not success_criteria:
        gaps.append("success_criteria_missing")

    if blockers:
        gaps.append("active_blockers_present")

    if not str(payload.get("deadline", "")).strip():
        gaps.append("deadline_missing")

    return gaps


def build_recommendation(status: str, gaps: List[str], priority_score: int) -> str:
    if status in {"cancelled"}:
        return "CANCEL"

    if status in {"paused"}:
        return "PAUSE"

    if "active_blockers_present" in gaps:
        return "UNBLOCK_FIRST"

    if status == "completed":
        return "PAUSE"

    if priority_score >= 65 and not gaps:
        return "EXECUTE_NOW"

    return "SCHEDULE"


def build_next_action(recommendation: str, gaps: List[str]) -> str:
    if recommendation == "EXECUTE_NOW":
        return "Begin execution and update status after the next work block."

    if recommendation == "UNBLOCK_FIRST":
        return "Resolve blockers before assigning more execution time."

    if recommendation == "SCHEDULE":
        if gaps:
            return "Complete missing mission fields before execution: " + ", ".join(gaps)
        return "Schedule this mission into the next sprint."

    if recommendation == "PAUSE":
        return "Hold mission until conditions change or AAR recommends restart."

    return "Cancel or archive this mission."


def create_mission(payload: Dict[str, Any]) -> Dict[str, Any]:
    title = payload.get("title", "Untitled Mission")
    objective = payload.get("objective", "")
    status = str(payload.get("status", "planned")).lower()

    if status not in MISSION_STATUSES:
        status = "planned"

    priority_score = calculate_priority_score(payload)
    priority_level = classify_priority(priority_score)
    gaps = detect_execution_gaps(payload)
    recommendation = build_recommendation(status, gaps, priority_score)

    mission = {
        "mission_id": build_mission_id(title, objective),
        "title": title,
        "objective": objective,
        "source": payload.get("source", "manual"),
        "owner": payload.get("owner", ""),
        "status": status,
        "priority_score": priority_score,
        "priority_level": priority_level,
        "recommendation": recommendation,
        "deadline": payload.get("deadline", ""),
        "success_criteria": normalize_list(payload.get("success_criteria")),
        "blockers": normalize_list(payload.get("blockers")),
        "dependencies": normalize_list(payload.get("dependencies")),
        "next_actions": normalize_list(payload.get("next_actions")),
        "execution_gaps": gaps,
        "ready_to_execute": recommendation == "EXECUTE_NOW",
        "created_at": utc_now(),
        "next_action": build_next_action(recommendation, gaps),
        "doctrine": MISSION_DOCTRINE,
    }

    if not mission["next_actions"]:
        mission["next_actions"] = [mission["next_action"]]

    return mission


def update_mission_status(payload: Dict[str, Any]) -> Dict[str, Any]:
    status = str(payload.get("status", "planned")).lower()
    if status not in MISSION_STATUSES:
        status = "planned"

    blockers = normalize_list(payload.get("blockers"))
    progress_notes = normalize_list(payload.get("progress_notes"))
    completed_criteria = normalize_list(payload.get("completed_criteria"))

    status_flags: List[str] = []

    if status == "blocked" and not blockers:
        status_flags.append("Blocked status requires listed blockers.")

    if status == "completed" and not completed_criteria:
        status_flags.append("Completed status should include completed success criteria.")

    if status == "active" and blockers:
        status_flags.append("Active mission has blockers that may need escalation.")

    if status == "completed":
        next_action = "Run AAR and capture lessons learned."
    elif status == "blocked":
        next_action = "Resolve or escalate blockers."
    elif status == "active":
        next_action = "Continue execution and update progress after next work block."
    elif status == "paused":
        next_action = "Define restart condition before resuming."
    elif status == "cancelled":
        next_action = "Archive mission and document why it was cancelled."
    else:
        next_action = "Schedule mission or complete missing planning fields."

    return {
        "mission_id": payload.get("mission_id", ""),
        "title": payload.get("title", "Untitled Mission"),
        "status": status,
        "progress_notes": progress_notes,
        "completed_criteria": completed_criteria,
        "blockers": blockers,
        "status_flags": status_flags,
        "updated_at": utc_now(),
        "next_action": next_action,
    }


def build_sprint_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    raw_missions = payload.get("missions", [])
    sprint_name = payload.get("sprint_name", "Unnamed Sprint")
    capacity = clamp_score(payload.get("capacity"))
    if capacity == 0:
        capacity = 5

    missions = []
    for item in raw_missions:
        if isinstance(item, dict):
            missions.append(create_mission(item))

    missions_sorted = sorted(
        missions,
        key=lambda mission: mission["priority_score"],
        reverse=True,
    )

    selected = missions_sorted[:capacity]
    deferred = missions_sorted[capacity:]

    risk_flags: List[str] = []

    if len(missions_sorted) > capacity:
        risk_flags.append("Sprint demand exceeds stated capacity.")

    if any(mission["execution_gaps"] for mission in selected):
        risk_flags.append("One or more selected missions have execution gaps.")

    if any(mission["blockers"] for mission in selected):
        risk_flags.append("One or more selected missions are blocked.")

    return {
        "sprint_name": sprint_name,
        "capacity": capacity,
        "selected_missions": selected,
        "deferred_missions": deferred,
        "risk_flags": risk_flags,
        "next_action": (
            "Execute selected missions in priority order."
            if selected
            else "No missions selected; add mission candidates."
        ),
        "doctrine": "Sprint planning converts intent into sequenced execution.",
    }


def generate_aar(payload: Dict[str, Any]) -> Dict[str, Any]:
    what_went_well = normalize_list(payload.get("what_went_well"))
    what_failed = normalize_list(payload.get("what_failed"))
    lessons_learned = normalize_list(payload.get("lessons_learned"))
    next_actions = normalize_list(payload.get("next_actions"))
    doctrine_updates = normalize_list(payload.get("doctrine_updates"))

    effectiveness_score = clamp_score(payload.get("effectiveness_score"))
    if effectiveness_score == 0 and (what_went_well or what_failed or lessons_learned):
        effectiveness_score = 5

    if effectiveness_score >= 8:
        result = "effective"
    elif effectiveness_score >= 5:
        result = "mixed"
    else:
        result = "ineffective"

    aar_flags: List[str] = []

    if not what_failed:
        aar_flags.append("No failures listed; AAR may be incomplete.")

    if not lessons_learned:
        aar_flags.append("No lessons learned captured.")

    if not next_actions:
        aar_flags.append("No next actions assigned.")

    return {
        "mission_id": payload.get("mission_id", ""),
        "title": payload.get("title", "Untitled Mission"),
        "result": result,
        "effectiveness_score": effectiveness_score,
        "what_went_well": what_went_well,
        "what_failed": what_failed,
        "lessons_learned": lessons_learned,
        "next_actions": next_actions,
        "doctrine_updates": doctrine_updates,
        "aar_flags": aar_flags,
        "completed_at": utc_now(),
        "next_action": (
            "Feed lessons learned back into strategy, daily brief, and future sprint planning."
        ),
        "doctrine": "Every completed mission must improve the system.",
    }
