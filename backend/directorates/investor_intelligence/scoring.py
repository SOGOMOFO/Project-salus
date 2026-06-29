from __future__ import annotations

from backend.directorates.investor_intelligence.models import EVIDENCE_QUALITY_GRADES


EVIDENCE_BASE_CONFIDENCE = {
    "A+": 95,
    "A": 90,
    "B": 80,
    "C": 70,
    "D": 60,
}

SCORE_WEIGHTS = {
    "valuation": 0.12,
    "financial_strength": 0.12,
    "growth": 0.14,
    "competitive_moat": 0.13,
    "management": 0.11,
    "macro_environment": 0.10,
    "technical_trend": 0.08,
    "risk": 0.10,
    "conviction": 0.10,
}


def compute_composite_score(scores: dict[str, int]) -> float:
    weighted = 0.0
    for field, weight in SCORE_WEIGHTS.items():
        if field == "risk":
            adjusted = 100 - scores[field]
            weighted += adjusted * weight
        else:
            weighted += scores[field] * weight
    return round(weighted, 2)


def compute_confidence(
    *,
    evidence_quality: str,
    has_thesis: bool,
    has_bear_case: bool,
    has_bull_case: bool,
    assumptions_count: int,
) -> int | str:
    quality = evidence_quality if evidence_quality in EVIDENCE_QUALITY_GRADES else "C"
    confidence = float(EVIDENCE_BASE_CONFIDENCE[quality])

    if has_thesis:
        confidence += 2
    if has_bear_case:
        confidence += 1
    if has_bull_case:
        confidence += 1
    confidence += min(3, assumptions_count)

    confidence = max(0.0, min(99.0, confidence))
    return band_confidence(confidence)


def band_confidence(confidence: float) -> int | str:
    if confidence >= 97:
        return 99
    if confidence >= 93:
        return 95
    if confidence >= 88:
        return 90
    if confidence >= 78:
        return 80
    if confidence >= 68:
        return 70
    if confidence >= 58:
        return 60
    return "below_60"


def confidence_to_number(confidence_band: int | str) -> int:
    if isinstance(confidence_band, int):
        return confidence_band
    return 50


def recommendation_for(
    *,
    composite_score: float,
    confidence_band: int | str,
    exceptional_risk_reward: bool,
    risk_score: int,
) -> str:
    confidence_numeric = confidence_to_number(confidence_band)

    if confidence_numeric < 80 and not exceptional_risk_reward:
        return "Monitor"

    if confidence_numeric < 80 and exceptional_risk_reward:
        return "Hold" if composite_score < 82 else "Buy"

    if composite_score >= 80 and risk_score <= 55:
        return "Buy"
    if composite_score >= 65 and risk_score <= 70:
        return "Hold"
    if composite_score < 45 or risk_score >= 82:
        return "Avoid"
    return "Monitor"
