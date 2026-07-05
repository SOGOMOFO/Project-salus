from typing import Any, Dict, List


RECOMMENDATIONS = ["PURSUE", "PAUSE", "DELEGATE", "DISCARD"]

EVIDENCE_LEVELS = {
    "verified_fact": 100,
    "strong_evidence": 85,
    "expert_opinion": 70,
    "emerging_theory": 50,
    "ai_generated_pattern": 35,
    "speculation": 20,
    "unverified_claim": 10,
}

REASONING_LENSES = [
    "objective_clarity",
    "assumption_quality",
    "evidence_quality",
    "strategic_fit",
    "roi",
    "risk",
    "difficulty",
    "opportunity_cost",
    "second_order_effects",
    "third_order_effects",
    "failure_modes",
    "execution_path",
]


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


def evidence_score(evidence_level: str) -> int:
    normalized = str(evidence_level or "unverified_claim").strip().lower()
    return EVIDENCE_LEVELS.get(normalized, 10)


def classify_evidence(evidence_level: str) -> Dict[str, Any]:
    normalized = str(evidence_level or "unverified_claim").strip().lower()
    if normalized not in EVIDENCE_LEVELS:
        normalized = "unverified_claim"

    score = EVIDENCE_LEVELS[normalized]

    if score >= 85:
        label = "strong"
    elif score >= 50:
        label = "moderate"
    elif score >= 20:
        label = "weak"
    else:
        label = "very_weak"

    return {
        "evidence_level": normalized,
        "evidence_score": score,
        "evidence_strength": label,
        "requires_verification": normalized in {
            "unverified_claim",
            "speculation",
            "ai_generated_pattern",
            "emerging_theory",
        },
    }


def analyze_assumptions(assumptions: List[str]) -> Dict[str, Any]:
    risk_flags: List[str] = []

    if not assumptions:
        return {
            "assumption_count": 0,
            "assumption_risk": "high",
            "risk_flags": ["No assumptions listed; hidden assumptions likely."],
            "recommended_action": "List the assumptions before committing resources.",
        }

    if len(assumptions) >= 6:
        risk_flags.append("High number of assumptions; plan may be fragile.")

    vague_terms = ["probably", "easy", "everyone", "always", "never", "guaranteed", "obvious", "simple"]
    for assumption in assumptions:
        lowered = assumption.lower()
        if any(term in lowered for term in vague_terms):
            risk_flags.append(f"Vague or overconfident assumption detected: {assumption}")

    if len(risk_flags) >= 3:
        risk = "high"
    elif risk_flags:
        risk = "medium"
    else:
        risk = "low"

    return {
        "assumption_count": len(assumptions),
        "assumption_risk": risk,
        "risk_flags": risk_flags,
        "recommended_action": "Validate the highest-risk assumption before scaling.",
    }


def generate_red_team(payload: Dict[str, Any]) -> Dict[str, Any]:
    title = payload.get("title", "Untitled Strategy")
    objective = payload.get("objective", "")
    assumptions = normalize_list(payload.get("assumptions"))
    constraints = normalize_list(payload.get("constraints"))
    dependencies = normalize_list(payload.get("dependencies"))
    failure_modes = normalize_list(payload.get("failure_modes"))
    evidence_against = normalize_list(payload.get("evidence_against"))

    attack_vectors: List[str] = []

    if not objective:
        attack_vectors.append("Objective is unclear; execution may optimize for the wrong outcome.")

    if not assumptions:
        attack_vectors.append("No assumptions provided; plan may contain unexamined risk.")

    for assumption in assumptions[:5]:
        attack_vectors.append(f"If this assumption is false, the plan weakens: {assumption}")

    for constraint in constraints[:5]:
        attack_vectors.append(f"Constraint may slow or block execution: {constraint}")

    for dependency in dependencies[:5]:
        attack_vectors.append(f"Dependency creates execution risk: {dependency}")

    for failure in failure_modes[:5]:
        attack_vectors.append(f"Known failure mode requires mitigation: {failure}")

    for item in evidence_against[:5]:
        attack_vectors.append(f"Counterevidence must be addressed: {item}")

    if not attack_vectors:
        attack_vectors.append("No major attack vectors supplied; perform external review before committing.")

    mitigation_actions = [
        "Define the measurable outcome.",
        "Validate the highest-risk assumption.",
        "Identify the smallest reversible test.",
        "Set a stop-loss condition.",
        "Run an AAR after the first execution cycle.",
    ]

    return {
        "title": title,
        "red_team_summary": "This review attacks the plan before resources are committed.",
        "attack_vectors": attack_vectors,
        "mitigation_actions": mitigation_actions,
        "enemy_vote": (
            "Reality, competitors, market conditions, time limits, family constraints, technical debt, "
            "and human behavior may all vote against the plan."
        ),
    }


def forecast_effects(payload: Dict[str, Any]) -> Dict[str, Any]:
    objective = payload.get("objective", "the proposed action")
    stakeholders = normalize_list(payload.get("stakeholders"))
    constraints = normalize_list(payload.get("constraints"))
    dependencies = normalize_list(payload.get("dependencies"))

    second_order = [
        f"If {objective} succeeds, it may create follow-on workload, maintenance, or governance requirements.",
        f"If {objective} consumes focus, other missions may slow down.",
    ]

    third_order = [
        f"If {objective} becomes part of the core system, it may shape future architecture and decision habits.",
        "A successful module can increase capability, but also increase complexity if not governed.",
    ]

    if stakeholders:
        second_order.append("Stakeholders affected: " + ", ".join(stakeholders[:5]) + ".")

    if constraints:
        second_order.append("Constraints may create delays or force scope reduction: " + ", ".join(constraints[:5]) + ".")

    if dependencies:
        third_order.append("Dependencies may create future fragility: " + ", ".join(dependencies[:5]) + ".")

    return {
        "second_order_effects": second_order,
        "third_order_effects": third_order,
        "doctrine": "Every major decision must consider consequences beyond the first move.",
    }


def calculate_reasoning_score(payload: Dict[str, Any]) -> int:
    objective = str(payload.get("objective", "")).strip()
    assumptions = normalize_list(payload.get("assumptions"))
    evidence_for = normalize_list(payload.get("evidence_for"))
    evidence_against = normalize_list(payload.get("evidence_against"))
    alternatives = normalize_list(payload.get("alternatives"))
    failure_modes = normalize_list(payload.get("failure_modes"))

    strategic_fit = clamp_score(payload.get("strategic_fit"))
    roi = clamp_score(payload.get("roi"))
    risk = clamp_score(payload.get("risk"))
    difficulty = clamp_score(payload.get("difficulty"))
    opportunity_cost = clamp_score(payload.get("opportunity_cost"))

    ev_score = evidence_score(payload.get("evidence_level", "unverified_claim")) / 10

    objective_score = 10 if objective else 0
    assumption_score = min(10, len(assumptions) * 2)
    evidence_balance_score = min(10, len(evidence_for) * 2 + len(evidence_against) * 2)
    alternatives_score = min(10, len(alternatives) * 3)
    failure_score = min(10, len(failure_modes) * 3)

    weighted = (
        objective_score * 0.12
        + assumption_score * 0.10
        + evidence_balance_score * 0.12
        + ev_score * 0.14
        + strategic_fit * 0.16
        + roi * 0.12
        + (10 - risk) * 0.10
        + (10 - difficulty) * 0.06
        + (10 - opportunity_cost) * 0.05
        + alternatives_score * 0.06
        + failure_score * 0.07
    )

    return round(max(0, min(weighted * 10, 100)))


def generate_recommendation(payload: Dict[str, Any], reasoning_score: int) -> str:
    strategic_fit = clamp_score(payload.get("strategic_fit"))
    roi = clamp_score(payload.get("roi"))
    risk = clamp_score(payload.get("risk"))
    opportunity_cost = clamp_score(payload.get("opportunity_cost"))
    difficulty = clamp_score(payload.get("difficulty"))
    ev = classify_evidence(payload.get("evidence_level"))

    if ev["evidence_level"] in {"unverified_claim", "speculation", "ai_generated_pattern"} and risk >= 7:
        return "DISCARD"

    if strategic_fit < 5 and opportunity_cost >= 6:
        return "DISCARD"

    if strategic_fit >= 7 and roi >= 7 and reasoning_score >= 70 and risk <= 6:
        return "PURSUE"

    if strategic_fit >= 6 and roi >= 7 and difficulty >= 7:
        return "DELEGATE"

    if reasoning_score >= 55:
        return "PAUSE"

    return "DISCARD"


def build_execution_plan(recommendation: str, payload: Dict[str, Any]) -> List[str]:
    if recommendation == "PURSUE":
        return [
            "Define the smallest executable version.",
            "Assign an owner.",
            "Set a measurable success condition.",
            "Set a stop-loss condition.",
            "Execute one controlled sprint.",
            "Run an AAR and update doctrine.",
        ]

    if recommendation == "PAUSE":
        return [
            "Move to holding queue.",
            "Identify missing evidence.",
            "Validate the riskiest assumption.",
            "Re-score after new information is collected.",
        ]

    if recommendation == "DELEGATE":
        return [
            "Remove from core Salus build path.",
            "Assign to outside support, automation, contractor, or later sprint.",
            "Track only if it supports current mission priorities.",
        ]

    return [
        "Archive or discard.",
        "Do not allocate active build time.",
        "Preserve only as a note if it may become useful later.",
    ]


def analyze_strategy(payload: Dict[str, Any]) -> Dict[str, Any]:
    assumptions = normalize_list(payload.get("assumptions"))
    evidence_for = normalize_list(payload.get("evidence_for"))
    evidence_against = normalize_list(payload.get("evidence_against"))
    constraints = normalize_list(payload.get("constraints"))
    dependencies = normalize_list(payload.get("dependencies"))
    alternatives = normalize_list(payload.get("alternatives"))
    failure_modes = normalize_list(payload.get("failure_modes"))
    stakeholders = normalize_list(payload.get("stakeholders"))

    evidence = classify_evidence(payload.get("evidence_level"))
    assumption_review = analyze_assumptions(assumptions)
    red_team = generate_red_team(payload)
    effects = forecast_effects(payload)
    reasoning_score = calculate_reasoning_score(payload)
    recommendation = generate_recommendation(payload, reasoning_score)
    execution_plan = build_execution_plan(recommendation, payload)

    warnings: List[str] = []

    if evidence["requires_verification"]:
        warnings.append("Evidence requires verification before operational commitment.")

    if assumption_review["assumption_risk"] == "high":
        warnings.append("Assumption risk is high.")

    if clamp_score(payload.get("risk")) >= 7:
        warnings.append("Risk score is high.")

    if clamp_score(payload.get("opportunity_cost")) >= 7:
        warnings.append("Opportunity cost is high.")

    if not alternatives:
        warnings.append("No alternatives listed; decision may be under-compared.")

    if not failure_modes:
        warnings.append("No failure modes listed; plan may be overconfident.")

    decision_memo = {
        "decision": recommendation,
        "why": build_why_statement(recommendation, payload, reasoning_score, evidence),
        "must_validate": build_validation_targets(assumptions, evidence, failure_modes),
        "smallest_next_step": execution_plan[0],
        "stop_loss": build_stop_loss(payload),
    }

    return {
        "title": payload.get("title", "Untitled Strategy"),
        "objective": payload.get("objective", ""),
        "reasoning_score": reasoning_score,
        "recommendation": recommendation,
        "evidence": evidence,
        "assumption_review": assumption_review,
        "red_team": red_team,
        "effects_forecast": effects,
        "inputs_reviewed": {
            "assumptions": assumptions,
            "evidence_for": evidence_for,
            "evidence_against": evidence_against,
            "constraints": constraints,
            "dependencies": dependencies,
            "alternatives": alternatives,
            "failure_modes": failure_modes,
            "stakeholders": stakeholders,
        },
        "warnings": warnings,
        "execution_plan": execution_plan,
        "decision_memo": decision_memo,
        "doctrine": (
            "Strategy is disciplined choice under constraint. Critical thinking is the act of attacking "
            "assumptions before reality does."
        ),
    }


def build_why_statement(
    recommendation: str,
    payload: Dict[str, Any],
    reasoning_score: int,
    evidence: Dict[str, Any],
) -> str:
    if recommendation == "PURSUE":
        return (
            f"Reasoning score is {reasoning_score}, evidence is {evidence['evidence_strength']}, "
            "and the idea appears strong enough for a controlled sprint."
        )

    if recommendation == "PAUSE":
        return (
            f"Reasoning score is {reasoning_score}. The idea may have value, but evidence, assumptions, "
            "risk, or execution clarity are not strong enough for full commitment."
        )

    if recommendation == "DELEGATE":
        return (
            "The idea may have ROI but should not consume core Salus build capacity unless it directly supports "
            "current mission priorities."
        )

    return (
        "The idea is too weak, risky, low-fit, or unsupported to justify active resources."
    )


def build_validation_targets(
    assumptions: List[str],
    evidence: Dict[str, Any],
    failure_modes: List[str],
) -> List[str]:
    targets: List[str] = []

    if evidence["requires_verification"]:
        targets.append("Verify the claim with stronger evidence.")

    if assumptions:
        targets.append("Test assumption: " + assumptions[0])
    else:
        targets.append("List and test hidden assumptions.")

    if failure_modes:
        targets.append("Mitigate failure mode: " + failure_modes[0])
    else:
        targets.append("Identify the most likely failure mode.")

    return targets


def build_stop_loss(payload: Dict[str, Any]) -> str:
    time_horizon = str(payload.get("time_horizon", "one sprint")).strip() or "one sprint"
    return (
        f"Stop or rescore after {time_horizon} if there is no measurable progress, "
        "evidence weakens, or opportunity cost becomes unacceptable."
    )
