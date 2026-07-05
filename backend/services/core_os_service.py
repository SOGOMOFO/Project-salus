from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List
from uuid import uuid4
import json


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

HEALTH_CHECKINS_FILE = DATA_DIR / "core_os_health_checkins.json"
BUSINESS_MISSIONS_FILE = DATA_DIR / "core_os_business_missions.json"


def now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


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


def reset_core_os_data() -> Dict[str, Any]:
    write_json(HEALTH_CHECKINS_FILE, [])
    write_json(BUSINESS_MISSIONS_FILE, [])

    return {
        "health_checkins": True,
        "business_missions": True,
    }


def health_status() -> Dict[str, Any]:
    checkins = read_json(HEALTH_CHECKINS_FILE, [])

    latest = checkins[-1] if checkins else None

    return {
        "module": "health",
        "status": "ok",
        "mission": "Improve Kyle's long-term physical capability, recovery, energy, and longevity.",
        "records": {
            "checkins": len(checkins),
        },
        "latest_checkin": latest,
        "tracked_domains": [
            "sleep",
            "fitness",
            "nutrition",
            "hydration",
            "surgery_recovery",
            "habits",
            "stress",
        ],
        "next_action": "Log a health check-in and identify the single highest-leverage physical action today.",
    }


def create_health_checkin(payload: Dict[str, Any]) -> Dict[str, Any]:
    record = {
        "id": str(payload.get("id") or uuid4()),
        "created_at": now_utc(),
        "sleep_quality": payload.get("sleep_quality", "not_assessed"),
        "energy": payload.get("energy", "not_assessed"),
        "training": payload.get("training", ""),
        "nutrition": payload.get("nutrition", ""),
        "hydration": payload.get("hydration", ""),
        "pain_or_symptoms": payload.get("pain_or_symptoms", ""),
        "recovery_focus": payload.get("recovery_focus", ""),
        "next_action": payload.get("next_action", ""),
    }

    append_record(HEALTH_CHECKINS_FILE, record)

    return record


def health_brief() -> Dict[str, Any]:
    status = health_status()
    latest = status["latest_checkin"]

    if latest and latest.get("next_action"):
        next_action = latest["next_action"]
    else:
        next_action = "Complete a basic health check-in today."

    return {
        "module": "health_brief",
        "status": "ok",
        "summary": "Health is treated as mission readiness, not a side project.",
        "latest_checkin": latest,
        "recommended_focus": [
            "sleep",
            "hydration",
            "movement",
            "nutrition",
            "recovery",
        ],
        "next_action": next_action,
    }


def business_status() -> Dict[str, Any]:
    missions = read_json(BUSINESS_MISSIONS_FILE, [])

    active = [
        mission for mission in missions
        if str(mission.get("status", "")).lower() not in {"done", "complete", "completed"}
    ]

    return {
        "module": "business",
        "status": "ok",
        "mission": "Build Echo Seven and Project Salus into durable assets that support financial freedom and family legacy.",
        "records": {
            "missions": len(missions),
            "active_missions": len(active),
        },
        "active_missions": active,
        "priority_domains": [
            "Echo Seven",
            "Project Salus",
            "government_contracting",
            "AI_governance",
            "cybersecurity_GRC",
            "local_service_businesses",
            "strategic_relationships",
        ],
        "next_action": active[0]["next_action"] if active else "Create one business mission with a clear next action.",
    }


def create_business_mission(payload: Dict[str, Any]) -> Dict[str, Any]:
    record = {
        "id": str(payload.get("id") or uuid4()),
        "created_at": now_utc(),
        "title": payload.get("title", "Untitled business mission"),
        "intent": payload.get("intent", ""),
        "domain": payload.get("domain", "general"),
        "priority": payload.get("priority", "medium"),
        "status": payload.get("status", "planned"),
        "risk": payload.get("risk", "not_assessed"),
        "next_action": payload.get("next_action", ""),
    }

    append_record(BUSINESS_MISSIONS_FILE, record)

    return record


def business_brief() -> Dict[str, Any]:
    status = business_status()

    return {
        "module": "business_brief",
        "status": "ok",
        "summary": "Business work should convert effort into assets, income, capability, or strategic positioning.",
        "records": status["records"],
        "active_missions": status["active_missions"],
        "next_action": status["next_action"],
    }


def legacy_status() -> Dict[str, Any]:
    return {
        "module": "legacy",
        "status": "ok",
        "mission": "Build, protect, and transfer capability, wealth, wisdom, and resilience across generations.",
        "doctrine": "The Barney Legacy Protocol evaluates major decisions across 1-, 5-, 10-, 25-, 50-, and 100-year horizons.",
        "tracked_domains": [
            "family_stability",
            "wealth_creation",
            "asset_protection",
            "education",
            "health",
            "business_ownership",
            "estate_planning",
            "values_and_wisdom_transfer",
        ],
        "next_action": "Identify one decision this week that improves the family's 10-year position.",
    }


def legacy_brief() -> Dict[str, Any]:
    return {
        "module": "legacy_brief",
        "status": "ok",
        "question": "If your great-grandchildren looked back 100 years from now, would this decision make them better off?",
        "recommended_focus": [
            "protect the family system",
            "create durable assets",
            "reduce fragile debt",
            "teach capability",
            "document decisions and lessons",
        ],
        "next_action": "Convert one current effort into a durable asset or documented lesson.",
    }


def command_readiness() -> Dict[str, Any]:
    health = health_status()
    business = business_status()
    legacy = legacy_status()

    scores = {
        "health": 70 if health["records"]["checkins"] else 50,
        "business": 75 if business["records"]["active_missions"] else 50,
        "legacy": 70,
        "family": 70,
        "education": 70,
    }

    overall = round(sum(scores.values()) / len(scores), 2)

    if overall >= 75:
        level = "green"
    elif overall >= 55:
        level = "amber"
    else:
        level = "red"

    return {
        "module": "command_readiness",
        "status": "ok",
        "overall_score": overall,
        "readiness_level": level,
        "scores": scores,
        "interpretation": "Readiness measures whether Kyle's core operating domains are being actively maintained.",
    }


def command_risks() -> Dict[str, Any]:
    health = health_status()
    business = business_status()

    risks: List[Dict[str, Any]] = []

    if not health["records"]["checkins"]:
        risks.append({
            "domain": "health",
            "risk": "no_recent_health_checkin",
            "severity": "medium",
            "recommended_action": "Log a health check-in.",
        })

    if not business["records"]["active_missions"]:
        risks.append({
            "domain": "business",
            "risk": "no_active_business_mission",
            "severity": "medium",
            "recommended_action": "Create one active business mission.",
        })

    risks.append({
        "domain": "execution",
        "risk": "feature_expansion_without_architecture_cleanup",
        "severity": "medium",
        "recommended_action": "Continue extracting routes and services while adding new capabilities.",
    })

    return {
        "module": "command_risks",
        "status": "ok",
        "count": len(risks),
        "risks": risks,
    }


def command_next_actions() -> Dict[str, Any]:
    health = health_status()
    business = business_status()
    legacy = legacy_status()

    return {
        "module": "command_next_actions",
        "status": "ok",
        "actions": [
            {
                "domain": "health",
                "action": health["next_action"],
            },
            {
                "domain": "business",
                "action": business["next_action"],
            },
            {
                "domain": "legacy",
                "action": legacy["next_action"],
            },
        ],
    }


def command_brief() -> Dict[str, Any]:
    readiness = command_readiness()
    risks = command_risks()
    next_actions = command_next_actions()

    return {
        "module": "command_brief",
        "status": "ok",
        "title": "Project Salus Command Brief",
        "readiness": readiness,
        "risks": risks,
        "next_actions": next_actions["actions"],
        "commander_intent": "Focus effort on the highest-leverage actions across health, family, school, business, and legacy.",
    }
