from __future__ import annotations

from backend.directorates.investor_intelligence.scoring import recommendation_for


def build_recommendation(
    *,
    composite_score: float,
    confidence_band: int | str,
    exceptional_risk_reward: bool,
    risk_score: int,
) -> str:
    return recommendation_for(
        composite_score=composite_score,
        confidence_band=confidence_band,
        exceptional_risk_reward=exceptional_risk_reward,
        risk_score=risk_score,
    )
