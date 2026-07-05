import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("data")

MISSION_FILE = DATA_DIR / "mission_registry_missions.json"
AAR_FILE = DATA_DIR / "mission_registry_aars.json"
DOCTRINE_FILE = DATA_DIR / "doctrine_registry_records.json"
LESSONS_FILE = DATA_DIR / "doctrine_registry_lessons.json"
PARKING_FILE = DATA_DIR / "curiosity_parking_lot_items.json"
WORKFLOW_FILE = DATA_DIR / "workflow_orchestrator_runs.json"

OPERATOR_CONSOLE_DOCTRINE = (
    "Project Salus must present one command-facing operating picture so Kyle can see status, "
    "risks, priorities, and next action without opening every module separately."
)

MODULE_CARDS = [
    {
        "key": "command_center",
        "name": "Command Center",
        "framework_endpoint": "/command-center/framework",
        "primary_endpoint": "/command-center/dashboard",
        "purpose": "Unified readiness, risks, mission status, and priority stack.",
    },
    {
        "key": "mission_registry",
        "name": "Mission Registry",
        "framework_endpoint": "/mission-registry/framework",
        "primary_endpoint": "/mission-registry/dashboard/summary",
        "purpose": "Persistent mission memory, status, blockers, and AAR links.",
    },
    {
        "key": "doctrine_registry",
        "name": "Doctrine Registry",
        "framework_endpoint": "/doctrine-registry/framework",
        "primary_endpoint": "/doctrine-registry/dashboard",
        "purpose": "Doctrine records, lessons learned, review status, and evidence levels.",
    },
    {
        "key": "intelligence_intake",
        "name": "Intelligence Intake",
        "framework_endpoint": "/intelligence-intake/framework",
        "primary_endpoint": "/intelligence-intake/triage",
        "purpose": "Classify raw information before action.",
    },
    {
        "key": "curiosity_parking_lot",
        "name": "Curiosity Parking Lot",
        "framework_endpoint": "/curiosity-parking-lot/framework",
        "primary_endpoint": "/curiosity-parking-lot/dashboard",
        "purpose": "Park, review, promote, discard, or archive low-certainty ideas.",
    },
    {
        "key": "workflow_orchestrator",
        "name": "Workflow Orchestrator",
        "framework_endpoint": "/workflow-orchestrator/framework",
        "primary_endpoint": "/workflow-orchestrator/dashboard",
        "purpose": "Move intelligence into mission, doctrine, parking, or discard.",
    },
    {
        "key": "build_accelerator",
        "name": "Build Accelerator",
        "framework_endpoint": "/build-accelerator/framework",
        "primary_endpoint": "/build-accelerator/system-map",
        "purpose": "Map build status, choose next build, plan sprints, and release cleanly.",
    },
    {
        "key": "decision_firewall",
        "name": "Decision Firewall",
        "framework_endpoint": "/decision-firewall/framework",
        "primary_endpoint": "/decision-firewall/analyze",
        "purpose": "Prevent bloat, weak-evidence action, and low-fit decisions.",
    },
    {
        "key": "strategy_critical_thinking",
        "name": "Strategy & Critical Thinking",
        "framework_endpoint": "/strategy-critical-thinking/framework",
        "primary_endpoint": "/strategy-critical-thinking/analyze",
        "purpose": "Assumptions, red-team review, second/third-order effects, and decision memos.",
    },
    {
        "key": "ai_governance",
        "name": "AI Governance",
        "framework_endpoint": "/ai-governance/framework",
        "primary_endpoint": "/ai-governance/assess-tool",
        "purpose": "Review AI tool risk, autonomy, access, logging, and controls.",
    },
    {
        "key": "wealth_os",
        "name": "Wealth OS",
        "framework_endpoint": "/wealth-os/framework",
        "primary_endpoint": "/wealth-os/classify-dollar",
        "purpose": "Classify cash and financial actions by mission value.",
    },
    {
        "key": "echo_seven_assessment",
        "name": "Echo Seven Assessment",
        "framework_endpoint": "/echo-seven/assessment/framework",
        "primary_endpoint": "/echo-seven/assessment/client-readiness",
        "purpose": "Package AI Governance & Cyber Readiness Assessment for clients.",
    },
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_json_list(path: Path) -> List[Dict[str, Any]]:
    if not path.exists():
        return []

    try:
        data = json.loads(path.read_text())
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    return [item for item in data if isinstance(item, dict)]


def file_exists(path: str) -> bool:
    return Path(path).exists()


def module_file_status(card: Dict[str, str]) -> Dict[str, Any]:
    key = card["key"]
    service_path = f"backend/services/{key}_service.py"
    route_path = f"backend/routes/{key}.py"
    test_path = f"tests/test_{key}_api.py"

    special_paths = {
        "echo_seven_assessment": {
            "service": "backend/services/echo_seven_assessment_service.py",
            "route": "backend/routes/echo_seven_assessment.py",
            "test": "tests/test_echo_seven_assessment_api.py",
        },
        "daily_brief_v2": {
            "service": "backend/services/daily_brief_service.py",
            "route": "backend/routes/daily_brief.py",
            "test": "tests/test_daily_brief_v2_api.py",
        },
    }

    if key in special_paths:
        service_path = special_paths[key]["service"]
        route_path = special_paths[key]["route"]
        test_path = special_paths[key]["test"]

    service_exists = file_exists(service_path)
    route_exists = file_exists(route_path)
    test_exists = file_exists(test_path)

    completion = round((int(service_exists) + int(route_exists) + int(test_exists)) / 3 * 100)

    if completion == 100:
        status = "implemented"
    elif completion > 0:
        status = "partial"
    else:
        status = "missing"

    return {
        **card,
        "service_path": service_path,
        "route_path": route_path,
        "test_path": test_path,
        "service_exists": service_exists,
        "route_exists": route_exists,
        "test_exists": test_exists,
        "completion": completion,
        "status": status,
    }


def mission_snapshot() -> Dict[str, Any]:
    missions = read_json_list(MISSION_FILE)
    aars = read_json_list(AAR_FILE)

    status_counts = {
        "planned": 0,
        "active": 0,
        "blocked": 0,
        "completed": 0,
        "paused": 0,
        "cancelled": 0,
    }

    blocked = []
    active = []

    for mission in missions:
        status = mission.get("status", "planned")
        if status in status_counts:
            status_counts[status] += 1
        if status == "blocked":
            blocked.append(mission)
        if status == "active":
            active.append(mission)

    top_missions = sorted(
        [mission for mission in missions if mission.get("status") not in {"completed", "cancelled"}],
        key=lambda item: item.get("priority_score", 0),
        reverse=True,
    )[:5]

    return {
        "total_missions": len(missions),
        "total_aars": len(aars),
        "status_counts": status_counts,
        "blocked_missions": blocked,
        "active_missions": active,
        "top_missions": top_missions,
    }


def doctrine_snapshot() -> Dict[str, Any]:
    doctrine = read_json_list(DOCTRINE_FILE)
    lessons = read_json_list(LESSONS_FILE)

    status_counts = {
        "proposed": 0,
        "active": 0,
        "needs_review": 0,
        "retired": 0,
    }

    weak_evidence = []
    review_needed = []

    for item in doctrine:
        status = item.get("status", "proposed")
        evidence = item.get("evidence_level", "unverified_claim")

        if status in status_counts:
            status_counts[status] += 1

        if status in {"proposed", "needs_review"}:
            review_needed.append(item)

        if evidence in {"speculation", "unverified_claim", "ai_generated_pattern"}:
            weak_evidence.append(item)

    return {
        "total_doctrine": len(doctrine),
        "total_lessons": len(lessons),
        "status_counts": status_counts,
        "review_needed_count": len(review_needed),
        "weak_evidence_count": len(weak_evidence),
        "review_needed": review_needed[:5],
    }


def parking_snapshot() -> Dict[str, Any]:
    items = read_json_list(PARKING_FILE)

    promote = [item for item in items if item.get("reconsideration_class") == "promote_candidate"]
    discard = [item for item in items if item.get("reconsideration_class") == "discard_candidate"]

    return {
        "total_items": len(items),
        "promote_candidates": sorted(promote, key=lambda item: item.get("reconsideration_score", 0), reverse=True)[:5],
        "discard_candidates": sorted(discard, key=lambda item: item.get("reconsideration_score", 0))[:5],
    }


def workflow_snapshot() -> Dict[str, Any]:
    runs = read_json_list(WORKFLOW_FILE)

    action_counts = {
        "triaged": 0,
        "parked": 0,
        "mission_created": 0,
        "doctrine_created": 0,
        "discarded": 0,
        "manual_review_required": 0,
    }

    for run in runs:
        for action in run.get("actions_taken", []):
            if action in action_counts:
                action_counts[action] += 1

    return {
        "total_runs": len(runs),
        "action_counts": action_counts,
        "latest_runs": sorted(runs, key=lambda item: item.get("created_at", ""), reverse=True)[:5],
    }


def module_snapshot() -> Dict[str, Any]:
    modules = [module_file_status(card) for card in MODULE_CARDS]

    implemented = [item for item in modules if item["status"] == "implemented"]
    partial = [item for item in modules if item["status"] == "partial"]
    missing = [item for item in modules if item["status"] == "missing"]

    completion_score = round(sum(item["completion"] for item in modules) / len(modules)) if modules else 0

    return {
        "total_modules": len(modules),
        "implemented_count": len(implemented),
        "partial_count": len(partial),
        "missing_count": len(missing),
        "completion_score": completion_score,
        "modules": modules,
        "partial_modules": partial,
        "missing_modules": missing,
    }


def build_risk_flags(
    modules: Dict[str, Any],
    missions: Dict[str, Any],
    doctrine: Dict[str, Any],
    parking: Dict[str, Any],
    workflows: Dict[str, Any],
) -> List[str]:
    flags = []

    if modules["partial_count"] > 0:
        flags.append("Partial modules detected; repair service/route/test mismatches.")

    if missions["blocked_missions"]:
        flags.append("Blocked missions require command attention.")

    if len(missions["active_missions"]) > 5:
        flags.append("Too many active missions may dilute focus.")

    if doctrine["review_needed_count"] > 0:
        flags.append("Doctrine records require review.")

    if doctrine["weak_evidence_count"] > 0:
        flags.append("Some doctrine has weak evidence.")

    if parking["promote_candidates"]:
        flags.append("Parking lot has items ready for promotion.")

    if parking["discard_candidates"]:
        flags.append("Parking lot has low-signal discard candidates.")

    if workflows["action_counts"]["manual_review_required"] > 0:
        flags.append("Workflow runs require manual review.")

    if not flags:
        flags.append("No major operator-console risk flags detected.")

    return flags


def build_next_action(
    modules: Dict[str, Any],
    missions: Dict[str, Any],
    doctrine: Dict[str, Any],
    parking: Dict[str, Any],
) -> str:
    if modules["partial_count"] > 0:
        first = modules["partial_modules"][0]
        return f"Repair partial module: {first['name']}."

    if missions["blocked_missions"]:
        first = missions["blocked_missions"][0]
        return f"Unblock mission: {first.get('title', 'Untitled Mission')}."

    if parking["promote_candidates"]:
        first = parking["promote_candidates"][0]
        return f"Review parked item for promotion: {first.get('title', 'Untitled Item')}."

    if doctrine["review_needed"]:
        first = doctrine["review_needed"][0]
        return f"Review doctrine candidate: {first.get('title', 'Untitled Doctrine')}."

    if missions["top_missions"]:
        first = missions["top_missions"][0]
        return f"Execute top mission: {first.get('title', 'Untitled Mission')}."

    return "Create or select the next highest-leverage mission."


def build_operator_overview(payload: Dict[str, Any]) -> Dict[str, Any]:
    modules = module_snapshot()
    missions = mission_snapshot()
    doctrine = doctrine_snapshot()
    parking = parking_snapshot()
    workflows = workflow_snapshot()

    risk_flags = build_risk_flags(modules, missions, doctrine, parking, workflows)
    next_action = build_next_action(modules, missions, doctrine, parking)

    readiness_score = calculate_readiness_score(modules, missions, doctrine, parking, workflows)

    return {
        "module": "operator_console_overview_v1",
        "generated_at": utc_now(),
        "commander_intent": payload.get("commander_intent") or (
            "Protect the family, increase capability, build durable wealth, govern risk, and execute the highest-leverage mission."
        ),
        "readiness": {
            "score": readiness_score,
            "level": readiness_level(readiness_score),
        },
        "modules": modules,
        "missions": missions,
        "doctrine_registry": doctrine,
        "curiosity_parking_lot": parking,
        "workflow_orchestrator": workflows,
        "risk_flags": risk_flags,
        "next_action": next_action,
        "doctrine": OPERATOR_CONSOLE_DOCTRINE,
    }


def calculate_readiness_score(
    modules: Dict[str, Any],
    missions: Dict[str, Any],
    doctrine: Dict[str, Any],
    parking: Dict[str, Any],
    workflows: Dict[str, Any],
) -> int:
    score = 100
    score -= modules["partial_count"] * 8
    score -= modules["missing_count"] * 4
    score -= len(missions["blocked_missions"]) * 10
    score -= doctrine["review_needed_count"] * 3
    score -= doctrine["weak_evidence_count"] * 2
    score -= len(parking["discard_candidates"]) * 1
    score -= workflows["action_counts"]["manual_review_required"] * 5

    return max(0, min(score, 100))


def readiness_level(score: int) -> str:
    if score >= 85:
        return "green"
    if score >= 65:
        return "amber"
    return "red"


def build_action_queue() -> Dict[str, Any]:
    overview = build_operator_overview({})
    actions: List[Dict[str, Any]] = []

    for module in overview["modules"]["partial_modules"]:
        actions.append({
            "type": "repair_module",
            "priority": "high",
            "target": module["name"],
            "action": f"Repair missing service/route/test for {module['name']}.",
        })

    for mission in overview["missions"]["blocked_missions"]:
        actions.append({
            "type": "unblock_mission",
            "priority": "high",
            "target": mission.get("title", "Untitled Mission"),
            "action": "Resolve blockers or pause mission.",
        })

    for item in overview["curiosity_parking_lot"]["promote_candidates"]:
        actions.append({
            "type": "review_promotion",
            "priority": "medium",
            "target": item.get("title", "Untitled Item"),
            "action": "Promote to mission/doctrine or keep parked.",
        })

    for item in overview["doctrine_registry"]["review_needed"]:
        actions.append({
            "type": "review_doctrine",
            "priority": "medium",
            "target": item.get("title", "Untitled Doctrine"),
            "action": "Promote, revise, or retire doctrine.",
        })

    for mission in overview["missions"]["top_missions"]:
        actions.append({
            "type": "execute_mission",
            "priority": "normal",
            "target": mission.get("title", "Untitled Mission"),
            "action": "Execute next mission step.",
        })

    if not actions:
        actions.append({
            "type": "maintain_readiness",
            "priority": "normal",
            "target": "Project Salus",
            "action": "Create or select the next highest-leverage mission.",
        })

    return {
        "module": "operator_console_action_queue_v1",
        "count": len(actions),
        "actions": actions[:15],
        "next_action": actions[0]["action"],
    }


def build_module_cards() -> Dict[str, Any]:
    cards = [module_file_status(card) for card in MODULE_CARDS]

    return {
        "module": "operator_console_module_cards_v1",
        "count": len(cards),
        "cards": cards,
    }


def build_health_check() -> Dict[str, Any]:
    overview = build_operator_overview({})
    score = overview["readiness"]["score"]
    level = overview["readiness"]["level"]

    return {
        "module": "operator_console_health_check_v1",
        "health_score": score,
        "health_level": level,
        "risk_flags": overview["risk_flags"],
        "next_action": overview["next_action"],
        "pass_condition": "Green if score >= 85, amber if 65-84, red if below 65.",
    }


def build_smoke_targets() -> Dict[str, Any]:
    endpoints = [card["framework_endpoint"] for card in MODULE_CARDS]
    endpoints.insert(0, "/operator-console/framework")
    endpoints.insert(1, "/operator-console/overview")
    endpoints.insert(2, "/operator-console/health")

    return {
        "module": "operator_console_smoke_targets_v1",
        "endpoints": endpoints,
        "commands": [
            "python3 -m backend.main",
            "pytest -q",
            "git status",
        ],
        "pass_condition": "Operator Console endpoints return 200 and full test suite passes.",
    }
