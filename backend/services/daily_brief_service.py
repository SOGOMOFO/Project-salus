from typing import Any, Dict, List


READINESS_AREAS = [
    "mission",
    "ai_governance",
    "wealth",
    "echo_seven",
    "family",
    "health",
    "learning",
]


def normalize_list(values: Any) -> List[str]:
    if not values:
        return []
    if isinstance(values, list):
        return [str(v).strip() for v in values if str(v).strip()]
    return [str(values).strip()]


def score_area(items: List[str], penalty_items: List[str], base: int = 85) -> int:
    score = base
    score -= len(items) * 5
    score -= len(penalty_items) * 8
    return max(0, min(score, 100))


def classify_readiness(score: int) -> str:
    if score >= 80:
        return "green"
    if score >= 60:
        return "amber"
    return "red"


def build_priority_stack(payload: Dict[str, Any]) -> List[Dict[str, str]]:
    priorities: List[Dict[str, str]] = []

    decisions_pending = normalize_list(payload.get("decisions_pending"))
    ai_tools = normalize_list(payload.get("ai_tools_requiring_review"))
    wealth_flags = normalize_list(payload.get("wealth_flags"))
    echo_targets = normalize_list(payload.get("echo_seven_targets"))
    top_objectives = normalize_list(payload.get("top_objectives"))

    if decisions_pending:
        priorities.append({
            "priority": "Run Decision Firewall",
            "reason": "Pending decisions must be filtered before execution.",
            "action": "Evaluate highest-impact pending decision first.",
        })

    if ai_tools:
        priorities.append({
            "priority": "Run AI Governance Review",
            "reason": "AI tools require safety controls before expanded use.",
            "action": "Assess the riskiest AI tool before deployment.",
        })

    if wealth_flags:
        priorities.append({
            "priority": "Assign Money Mission",
            "reason": "Unassigned cash or unresolved debt creates drift.",
            "action": "Use Wealth OS to classify and allocate available cash.",
        })

    if echo_targets:
        priorities.append({
            "priority": "Advance Echo Seven Offer",
            "reason": "Revenue validation is higher leverage than theory.",
            "action": "Move one target toward a starter snapshot or readiness assessment.",
        })

    for objective in top_objectives[:2]:
        priorities.append({
            "priority": objective,
            "reason": "Listed as a top objective for the current brief.",
            "action": "Define the smallest executable next step.",
        })

    if not priorities:
        priorities.append({
            "priority": "Maintain Mission Readiness",
            "reason": "No major blockers were reported.",
            "action": "Execute the top scheduled mission and log an AAR.",
        })

    return priorities[:5]


def generate_daily_brief(payload: Dict[str, Any]) -> Dict[str, Any]:
    active_risks = normalize_list(payload.get("active_risks"))
    constraints = normalize_list(payload.get("constraints"))
    decisions_pending = normalize_list(payload.get("decisions_pending"))
    ai_tools = normalize_list(payload.get("ai_tools_requiring_review"))
    wealth_flags = normalize_list(payload.get("wealth_flags"))
    echo_targets = normalize_list(payload.get("echo_seven_targets"))
    family_focus = normalize_list(payload.get("family_focus"))
    health_focus = normalize_list(payload.get("health_focus"))
    learning_focus = normalize_list(payload.get("learning_focus"))
    top_objectives = normalize_list(payload.get("top_objectives"))

    mission_score = score_area(active_risks, constraints, base=88)
    ai_score = score_area(ai_tools, active_risks, base=90)
    wealth_score = score_area(wealth_flags, constraints, base=86)
    echo_score = score_area([], constraints, base=78 if echo_targets else 70)
    family_score = score_area([], active_risks, base=82 if family_focus else 75)
    health_score = score_area([], constraints, base=82 if health_focus else 75)
    learning_score = score_area([], constraints, base=84 if learning_focus else 76)

    area_scores = {
        "mission": mission_score,
        "ai_governance": ai_score,
        "wealth": wealth_score,
        "echo_seven": echo_score,
        "family": family_score,
        "health": health_score,
        "learning": learning_score,
    }

    overall_score = round(sum(area_scores.values()) / len(area_scores))
    readiness_level = classify_readiness(overall_score)

    warnings: List[str] = []

    if decisions_pending:
        warnings.append("Pending decisions require Decision Firewall review.")

    if ai_tools:
        warnings.append("AI tools require governance review before expanded use.")

    if wealth_flags:
        warnings.append("Wealth flags require cash assignment or debt review.")

    if active_risks:
        warnings.append("Active risks require mitigation tracking.")

    if constraints:
        warnings.append("Constraints may limit execution capacity.")

    priority_stack = build_priority_stack(payload)

    return {
        "brief_name": "Project Salus Daily Commander Brief",
        "date": payload.get("date", "unspecified"),
        "commander_intent": payload.get("commander_intent") or (
            "Increase capability, protect the family, build durable wealth, and execute the highest-leverage mission."
        ),
        "overall_readiness_score": overall_score,
        "readiness_level": readiness_level,
        "area_scores": area_scores,
        "top_objectives": top_objectives,
        "priority_stack": priority_stack,
        "risk_register": {
            "active_risks": active_risks,
            "constraints": constraints,
            "warnings": warnings,
        },
        "focus_blocks": {
            "echo_seven": echo_targets,
            "family": family_focus,
            "health": health_focus,
            "learning": learning_focus,
        },
        "next_action": priority_stack[0]["action"],
        "doctrine": (
            "The Daily Brief converts information into ranked action, risk awareness, "
            "and measurable execution."
        ),
    }
