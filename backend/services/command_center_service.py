import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


MISSION_FILE = Path("data") / "mission_registry_missions.json"
AAR_FILE = Path("data") / "mission_registry_aars.json"

COMMAND_CENTER_DOCTRINE = (
    "Project Salus must convert intelligence, risk, strategy, and missions into one command view "
    "so Kyle can act without chasing scattered information."
)

COMMAND_MODULES = [
    "decision_firewall",
    "strategy_critical_thinking",
    "ai_governance",
    "wealth_os",
    "echo_seven_assessment",
    "daily_commander_brief",
    "mission_execution",
    "mission_registry",
    "command_center",
]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_list(values: Any) -> List[str]:
    if not values:
        return []
    if isinstance(values, list):
        return [str(v).strip() for v in values if str(v).strip()]
    return [str(values).strip()]


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


def clamp_score(value: Any) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(score, 100))


def readiness_level(score: int) -> str:
    if score >= 85:
        return "green"
    if score >= 65:
        return "amber"
    return "red"


def module_status_from_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    enabled_modules = set(normalize_list(payload.get("enabled_modules")))
    known_modules = set(COMMAND_MODULES)

    if not enabled_modules:
        enabled_modules = known_modules

    missing = sorted(known_modules - enabled_modules)
    active = sorted(enabled_modules & known_modules)

    module_scores: Dict[str, int] = {}

    for module in COMMAND_MODULES:
        if module in enabled_modules:
            module_scores[module] = 100
        else:
            module_scores[module] = 0

    return {
        "active_modules": active,
        "missing_modules": missing,
        "module_scores": module_scores,
        "module_coverage_score": round(sum(module_scores.values()) / len(module_scores)),
    }


def mission_registry_snapshot() -> Dict[str, Any]:
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

    blocked_missions: List[Dict[str, Any]] = []
    active_missions: List[Dict[str, Any]] = []
    top_priority_missions: List[Dict[str, Any]] = []

    for mission in missions:
        status = mission.get("status", "planned")
        if status in status_counts:
            status_counts[status] += 1

        if status == "blocked":
            blocked_missions.append(mission)

        if status == "active":
            active_missions.append(mission)

    top_priority_missions = sorted(
        [
            mission
            for mission in missions
            if mission.get("status") not in {"completed", "cancelled"}
        ],
        key=lambda item: item.get("priority_score", 0),
        reverse=True,
    )[:5]

    return {
        "total_missions": len(missions),
        "total_aars": len(aars),
        "status_counts": status_counts,
        "blocked_missions": blocked_missions,
        "active_missions": active_missions,
        "top_priority_missions": top_priority_missions,
    }


def build_risk_register(payload: Dict[str, Any], mission_snapshot: Dict[str, Any]) -> Dict[str, Any]:
    reported_risks = normalize_list(payload.get("reported_risks"))
    constraints = normalize_list(payload.get("constraints"))
    ai_tools_requiring_review = normalize_list(payload.get("ai_tools_requiring_review"))
    wealth_flags = normalize_list(payload.get("wealth_flags"))
    open_decisions = normalize_list(payload.get("open_decisions"))

    risk_flags: List[str] = []

    if mission_snapshot["blocked_missions"]:
        risk_flags.append("Blocked missions require command attention.")

    if len(mission_snapshot["active_missions"]) > 5:
        risk_flags.append("Too many active missions may dilute execution focus.")

    if ai_tools_requiring_review:
        risk_flags.append("AI tools require governance review.")

    if wealth_flags:
        risk_flags.append("Wealth flags require Wealth OS review.")

    if open_decisions:
        risk_flags.append("Open decisions require Decision Firewall or Strategy Directorate review.")

    if constraints:
        risk_flags.append("Constraints may reduce execution capacity.")

    if reported_risks:
        risk_flags.append("Reported risks require mitigation tracking.")

    risk_score = 100
    risk_score -= len(mission_snapshot["blocked_missions"]) * 12
    risk_score -= len(ai_tools_requiring_review) * 10
    risk_score -= len(wealth_flags) * 8
    risk_score -= len(open_decisions) * 6
    risk_score -= len(constraints) * 5
    risk_score -= len(reported_risks) * 5

    risk_score = max(0, min(risk_score, 100))

    return {
        "risk_score": risk_score,
        "risk_level": readiness_level(risk_score),
        "reported_risks": reported_risks,
        "constraints": constraints,
        "ai_tools_requiring_review": ai_tools_requiring_review,
        "wealth_flags": wealth_flags,
        "open_decisions": open_decisions,
        "risk_flags": risk_flags,
    }


def build_priority_stack(payload: Dict[str, Any], mission_snapshot: Dict[str, Any]) -> List[Dict[str, str]]:
    priorities: List[Dict[str, str]] = []

    blocked = mission_snapshot["blocked_missions"]
    top_missions = mission_snapshot["top_priority_missions"]

    if blocked:
        first = blocked[0]
        priorities.append({
            "priority": "Unblock mission",
            "target": first.get("title", "Blocked Mission"),
            "reason": "Blocked work prevents execution flow.",
            "action": "Resolve or escalate the listed blockers.",
        })

    ai_tools = normalize_list(payload.get("ai_tools_requiring_review"))
    if ai_tools:
        priorities.append({
            "priority": "Run AI governance review",
            "target": ai_tools[0],
            "reason": "AI tools should not receive unchecked authority.",
            "action": "Assess the highest-risk AI tool before expanded use.",
        })

    open_decisions = normalize_list(payload.get("open_decisions"))
    if open_decisions:
        priorities.append({
            "priority": "Run decision review",
            "target": open_decisions[0],
            "reason": "Unreviewed decisions create drift and bloat.",
            "action": "Send the decision through Decision Firewall or Strategy Directorate.",
        })

    wealth_flags = normalize_list(payload.get("wealth_flags"))
    if wealth_flags:
        priorities.append({
            "priority": "Run Wealth OS review",
            "target": wealth_flags[0],
            "reason": "Money without a mission creates leakage.",
            "action": "Classify and allocate cash or debt action.",
        })

    echo_targets = normalize_list(payload.get("echo_seven_targets"))
    if echo_targets:
        priorities.append({
            "priority": "Advance Echo Seven",
            "target": echo_targets[0],
            "reason": "Revenue validation turns Salus capability into business value.",
            "action": "Move one target toward a starter snapshot or readiness assessment.",
        })

    for mission in top_missions:
        if len(priorities) >= 7:
            break
        priorities.append({
            "priority": "Execute mission",
            "target": mission.get("title", "Untitled Mission"),
            "reason": f"Priority score {mission.get('priority_score', 0)}.",
            "action": mission.get("next_actions", ["Execute next mission step."])[0]
            if mission.get("next_actions")
            else "Execute next mission step.",
        })

    if not priorities:
        priorities.append({
            "priority": "Maintain readiness",
            "target": "Project Salus",
            "reason": "No critical blockers detected.",
            "action": "Execute the highest-value planned work block and log progress.",
        })

    return priorities[:7]


def calculate_command_readiness(
    module_status: Dict[str, Any],
    risk_register: Dict[str, Any],
    mission_snapshot: Dict[str, Any],
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    manual_score = payload.get("manual_readiness_score")

    if manual_score is not None:
        overall = clamp_score(manual_score)
    else:
        mission_score = 100
        mission_score -= len(mission_snapshot["blocked_missions"]) * 15
        mission_score -= max(0, len(mission_snapshot["active_missions"]) - 5) * 8
        mission_score = max(0, min(mission_score, 100))

        overall = round(
            module_status["module_coverage_score"] * 0.25
            + risk_register["risk_score"] * 0.35
            + mission_score * 0.25
            + 85 * 0.15
        )

    return {
        "overall_readiness_score": overall,
        "readiness_level": readiness_level(overall),
        "interpretation": build_readiness_interpretation(overall),
    }


def build_readiness_interpretation(score: int) -> str:
    if score >= 85:
        return "Command system is ready for execution. Maintain discipline and avoid expanding scope unnecessarily."

    if score >= 65:
        return "Command system is functional but needs focused risk reduction before expanding scope."

    return "Command system is degraded. Resolve blockers, reduce risk, and simplify execution."


def build_command_dashboard(payload: Dict[str, Any]) -> Dict[str, Any]:
    module_status = module_status_from_payload(payload)
    mission_snapshot = mission_registry_snapshot()
    risk_register = build_risk_register(payload, mission_snapshot)
    command_readiness = calculate_command_readiness(
        module_status=module_status,
        risk_register=risk_register,
        mission_snapshot=mission_snapshot,
        payload=payload,
    )
    priority_stack = build_priority_stack(payload, mission_snapshot)

    return {
        "module": "command_center_orchestrator_v1",
        "generated_at": utc_now(),
        "commander_intent": payload.get("commander_intent") or (
            "Protect the family, increase capability, build durable wealth, govern risk, and execute the highest-leverage mission."
        ),
        "command_readiness": command_readiness,
        "module_status": module_status,
        "mission_snapshot": mission_snapshot,
        "risk_register": risk_register,
        "priority_stack": priority_stack,
        "first_action": priority_stack[0]["action"],
        "doctrine": COMMAND_CENTER_DOCTRINE,
    }


def build_morning_brief(payload: Dict[str, Any]) -> Dict[str, Any]:
    dashboard = build_command_dashboard(payload)

    top_priorities = dashboard["priority_stack"][:3]
    risk_flags = dashboard["risk_register"]["risk_flags"]

    brief_lines: List[str] = []

    brief_lines.append("Commander intent: " + dashboard["commander_intent"])
    brief_lines.append(
        "Readiness: "
        + dashboard["command_readiness"]["readiness_level"]
        + " / "
        + str(dashboard["command_readiness"]["overall_readiness_score"])
    )

    if risk_flags:
        brief_lines.append("Primary risk: " + risk_flags[0])
    else:
        brief_lines.append("Primary risk: no critical risk reported.")

    if top_priorities:
        brief_lines.append("First action: " + top_priorities[0]["action"])

    return {
        "brief_name": "Project Salus Morning Command Brief",
        "generated_at": utc_now(),
        "readiness": dashboard["command_readiness"],
        "top_priorities": top_priorities,
        "risk_flags": risk_flags,
        "brief_lines": brief_lines,
        "doctrine": "The morning brief must produce action, not just awareness.",
    }


def build_module_health(payload: Dict[str, Any]) -> Dict[str, Any]:
    module_status = module_status_from_payload(payload)
    mission_snapshot = mission_registry_snapshot()

    health_flags: List[str] = []

    if module_status["missing_modules"]:
        health_flags.append("Some expected command modules are missing or disabled.")

    if mission_snapshot["total_missions"] == 0:
        health_flags.append("No registered missions found; execution memory is empty.")

    if mission_snapshot["total_missions"] > 0 and mission_snapshot["total_aars"] == 0:
        health_flags.append("Missions exist without AAR history.")

    return {
        "module": "command_center_module_health",
        "module_status": module_status,
        "mission_memory": {
            "total_missions": mission_snapshot["total_missions"],
            "total_aars": mission_snapshot["total_aars"],
        },
        "health_flags": health_flags,
        "next_action": (
            "Register at least one active mission."
            if mission_snapshot["total_missions"] == 0
            else "Keep mission status and AAR history current."
        ),
    }
