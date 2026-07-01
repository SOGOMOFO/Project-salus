from typing import Any


def explain_recommendation(judgment: dict[str, Any]) -> dict[str, Any]:
    recommendation = judgment.get("recommendation", "Monitor")
    score = judgment.get("score", 0)
    confidence = judgment.get("confidence", "below_60")
    risk = judgment.get("risk", {})
    top_risks = risk.get("top_risks", [])
    mitigation_required = risk.get("mitigation_required", False)

    reasons = []

    reasons.append(
        f"Recommendation is {recommendation} based on a weighted score of {score}."
    )

    reasons.append(f"Confidence level is {confidence}.")

    if top_risks:
        risk_names = ", ".join(item["category"] for item in top_risks)
        reasons.append(f"Primary risks are: {risk_names}.")

    if mitigation_required:
        reasons.append("Mitigation is required before execution.")

    why_not = {
        "Pursue": "Do not pursue unless score is high, confidence is strong, and risks are controlled.",
        "Pause": "Pause is appropriate when risk, uncertainty, or missing information prevents immediate action.",
        "Delegate": "Delegate is appropriate when value exists but execution is better handled by another person or system.",
        "Monitor": "Monitor is appropriate when the opportunity is not ready but should remain visible.",
        "Discard": "Discard is appropriate when risk, low evidence, or poor strategic fit makes the option unjustified.",
    }

    change_conditions = [
        "Increase evidence quality.",
        "Reduce top risk categories.",
        "Improve strategic fit.",
        "Improve ROI.",
        "Reduce difficulty or execution burden.",
        "Clarify timeline.",
    ]

    return {
        "recommendation": recommendation,
        "explanation": reasons,
        "why_not_other_options": why_not,
        "what_would_change_the_decision": change_conditions,
    }