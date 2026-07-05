from typing import Any, Dict, List

ALLOWED_OUTPUT_TYPES = {
    "doctrine",
    "feature",
    "checklist",
    "service_offer",
    "training_module",
    "dashboard",
    "report",
    "discard",
}

EVIDENCE_LEVELS = {
    "verified_fact": 100,
    "strong_evidence": 85,
    "expert_opinion": 70,
    "emerging_theory": 50,
    "ai_generated_pattern": 35,
    "speculation": 20,
    "unverified_claim": 10,
}


def clamp_score(value: Any) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(score, 10))


def classify_evidence(evidence_type: str) -> Dict[str, Any]:
    normalized = (evidence_type or "unverified_claim").strip().lower()
    if normalized not in EVIDENCE_LEVELS:
        normalized = "unverified_claim"

    return {
        "evidence_type": normalized,
        "evidence_score": EVIDENCE_LEVELS[normalized],
        "requires_verification": normalized in {
            "emerging_theory",
            "ai_generated_pattern",
            "speculation",
            "unverified_claim",
        },
    }


def run_no_bloat_gate(item: Dict[str, Any]) -> Dict[str, Any]:
    strategic_fit = clamp_score(item.get("strategic_fit"))
    actionability = clamp_score(item.get("actionability"))
    roi = clamp_score(item.get("roi"))
    risk = clamp_score(item.get("risk"))
    output_type = (item.get("output_type") or "").strip().lower()
    owner = (item.get("owner") or "").strip()

    failures: List[str] = []

    if strategic_fit < 6:
        failures.append("Low strategic fit.")
    if actionability < 6:
        failures.append("Not actionable enough.")
    if roi < 5:
        failures.append("Weak ROI.")
    if risk >= 8:
        failures.append("Risk level too high for default implementation.")
    if output_type not in ALLOWED_OUTPUT_TYPES:
        failures.append("Does not map to an approved Salus output type.")
    if not owner:
        failures.append("No owner assigned.")

    return {
        "passed": len(failures) == 0,
        "failures": failures,
        "approved_output_types": sorted(ALLOWED_OUTPUT_TYPES),
    }


def calculate_decision_score(item: Dict[str, Any]) -> int:
    strategic_fit = clamp_score(item.get("strategic_fit"))
    roi = clamp_score(item.get("roi"))
    actionability = clamp_score(item.get("actionability"))
    difficulty = clamp_score(item.get("difficulty"))
    risk = clamp_score(item.get("risk"))
    opportunity_cost = clamp_score(item.get("opportunity_cost"))

    evidence = classify_evidence(item.get("evidence_type", "unverified_claim"))
    evidence_normalized = evidence["evidence_score"] / 10

    weighted_score = (
        strategic_fit * 0.25
        + roi * 0.20
        + actionability * 0.20
        + evidence_normalized * 0.15
        + (10 - difficulty) * 0.07
        + (10 - risk) * 0.08
        + (10 - opportunity_cost) * 0.05
    )

    return round(weighted_score * 10)


def generate_recommendation(item: Dict[str, Any], score: int, gate: Dict[str, Any]) -> str:
    strategic_fit = clamp_score(item.get("strategic_fit"))
    roi = clamp_score(item.get("roi"))
    difficulty = clamp_score(item.get("difficulty"))
    risk = clamp_score(item.get("risk"))
    evidence_type = classify_evidence(item.get("evidence_type"))["evidence_type"]

    if evidence_type in {"unverified_claim", "speculation", "ai_generated_pattern"} and risk >= 6:
        return "DISCARD"

    if not gate["passed"]:
        if roi >= 7 and strategic_fit >= 6 and difficulty >= 7:
            return "DELEGATE"
        return "PAUSE"

    if score >= 75:
        return "PURSUE"

    if score >= 55:
        return "PAUSE"

    if roi >= 7 and strategic_fit < 6:
        return "DELEGATE"

    return "DISCARD"


def build_next_action(recommendation: str, item: Dict[str, Any]) -> str:
    output_type = (item.get("output_type") or "").strip().lower()

    if recommendation == "PURSUE":
        return f"Convert into a concrete {output_type} with owner, deadline, and measurable output."

    if recommendation == "PAUSE":
        return "Move to Curiosity Parking Lot until evidence, ROI, or actionability improves."

    if recommendation == "DELEGATE":
        return "Assign outside Salus core build unless it directly supports current mission priorities."

    return "Discard or archive. Do not spend active build time on this."


def evaluate_decision(item: Dict[str, Any]) -> Dict[str, Any]:
    evidence = classify_evidence(item.get("evidence_type", "unverified_claim"))
    gate = run_no_bloat_gate(item)
    score = calculate_decision_score(item)
    recommendation = generate_recommendation(item, score, gate)

    risk_flags: List[str] = []

    if evidence["requires_verification"]:
        risk_flags.append("Requires verification before operational use.")
    if clamp_score(item.get("risk")) >= 7:
        risk_flags.append("High risk.")
    if clamp_score(item.get("opportunity_cost")) >= 7:
        risk_flags.append("High opportunity cost.")
    if (item.get("output_type") or "").strip().lower() == "discard":
        risk_flags.append("Marked as discard output.")

    return {
        "title": item.get("title", "Untitled Decision"),
        "category": item.get("category", "general"),
        "decision_score": score,
        "recommendation": recommendation,
        "evidence": evidence,
        "no_bloat_gate": gate,
        "risk_flags": risk_flags,
        "salus_doctrine": (
            "Every idea must become doctrine, feature, checklist, service offer, "
            "training module, dashboard, report, or be discarded."
        ),
        "next_action": build_next_action(recommendation, item),
    }
