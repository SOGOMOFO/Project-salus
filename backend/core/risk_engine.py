from typing import Any


RISK_CATEGORIES = [
    "mission",
    "financial",
    "security",
    "legal",
    "operational",
    "reputation",
    "technical",
    "schedule",
    "human",
    "opportunity_cost",
]


def _normalize_score(value: Any, default: float = 50.0) -> float:
    """Normalize any numeric input to a score between 0 and 100."""
    try:
        score = float(value)
    except (TypeError, ValueError):
        score = default

    return max(0.0, min(100.0, score))


def risk_band(score: float) -> str:
    """Convert a numeric score into a human-readable risk band."""
    score = _normalize_score(score)

    if score >= 85:
        return "critical"
    elif score >= 70:
        return "high"
    elif score >= 50:
        return "moderate"
    elif score >= 30:
        return "guarded"
    else:
        return "low"


def assess_risk(risks: dict[str, Any]) -> dict[str, Any]:
    """
    Assess overall mission risk based on multiple risk categories.
    """

    category_scores: dict[str, float] = {}

    for category in RISK_CATEGORIES:
        category_scores[category] = _normalize_score(
            risks.get(category, 50.0)
        )

    overall_score = sum(category_scores.values()) / len(category_scores)

    top_risks = sorted(
        category_scores.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:3]

    mitigation_required = (
        overall_score >= 70
        or any(score >= 70 for _, score in top_risks)
    )

    return {
        "overall_score": round(overall_score, 2),
        "overall_band": risk_band(overall_score),
        "category_scores": category_scores,
        "top_risks": [
            {
                "category": category,
                "score": round(score, 2),
                "band": risk_band(score),
            }
            for category, score in top_risks
        ],
        "mitigation_required": mitigation_required,
    }


def recommend_risk_response(score: float) -> str:
    """
    Recommend an action based on overall risk.
    """

    band = risk_band(score)

    if band == "critical":
        return (
            "STOP. Commander review is required before proceeding. "
            "Mitigation plans must be completed."
        )

    elif band == "high":
        return (
            "Proceed only after mitigation plans, ownership assignment, "
            "and continuous monitoring are in place."
        )

    elif band == "moderate":
        return (
            "Proceed cautiously with documented controls and periodic review."
        )

    elif band == "guarded":
        return (
            "Risk is acceptable. Monitor during execution."
        )

    else:
        return (
            "Low risk. Proceed if aligned with mission objectives."
        )