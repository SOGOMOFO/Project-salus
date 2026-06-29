from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from statistics import mean
from typing import Any

AGENT_PANEL = [
    "Value Analyst",
    "Growth Analyst",
    "Macro Strategist",
    "Behavioral Economist",
    "Risk Officer",
    "Portfolio Manager",
]

INVESTMENT_METRICS = [
    "valuation",
    "financial_strength",
    "growth",
    "moat",
    "management",
    "macro",
    "technical",
    "risk",
    "conviction",
]

RECOMMENDATION_STATUSES = ["Buy", "Hold", "Monitor", "Avoid"]


@dataclass
class InvestorIntelligenceDirectorate:
    name: str = "Investor Intelligence Directorate"
    version: str = "v1"
    mode: str = "educational-decision-support"

    def status(self) -> dict[str, Any]:
        return {
            "status": "operational",
            "directorate": self.name,
            "version": self.version,
            "mode": self.mode,
            "agent_panel": AGENT_PANEL,
            "advice_notice": (
                "Outputs are educational and decision-support oriented, not certain financial advice."
            ),
        }

    def framework(self) -> dict[str, Any]:
        return {
            "directorate": self.name,
            "agent_panel": AGENT_PANEL,
            "scoring_model": {
                "metrics": INVESTMENT_METRICS,
                "score_scale": "0-100",
                "confidence_scale": "0-100",
                "decision_rules": [
                    "Default to Monitor when confidence < 80 unless risk/reward is exceptional.",
                    "Favor Avoid for weak conviction with elevated risk.",
                    "Use Buy and Hold only when evidence quality is sufficient.",
                ],
            },
            "recommendation_statuses": RECOMMENDATION_STATUSES,
            "constraints": {
                "brokerage_connections": "disabled",
                "certainty_language": "prohibited",
            },
        }

    def analyze(self, payload: dict[str, Any]) -> dict[str, Any]:
        ticker = str(payload.get("ticker", "")).strip().upper() or "UNKNOWN"
        scores = self._normalize_scores(payload.get("scores", {}))
        confidence = _clamp_0_100(payload.get("confidence", mean(scores.values())))

        avg_score = round(mean(scores.values()), 2)
        risk_score = scores["risk"]
        reward_proxy = round((scores["growth"] + scores["moat"] + scores["conviction"]) / 3.0, 2)
        risk_reward_gap = round(reward_proxy - risk_score, 2)
        exceptional_risk_reward = risk_reward_gap >= 18 and scores["conviction"] >= 75

        recommendation = self._recommendation(
            average_score=avg_score,
            confidence=confidence,
            risk_score=risk_score,
            exceptional_risk_reward=exceptional_risk_reward,
        )

        rationale = [
            f"Composite score is {avg_score} across the nine-factor framework.",
            f"Estimated confidence is {confidence}% based on submitted evidence.",
            f"Risk/reward gap is {risk_reward_gap} (higher is better).",
        ]
        if confidence < 80 and not exceptional_risk_reward:
            rationale.append(
                "Recommendation defaults to Monitor because confidence is below 80% and risk/reward is not exceptional."
            )

        return {
            "status": "ok",
            "directorate": self.name,
            "ticker": ticker,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "scores": scores,
            "confidence": confidence,
            "recommendation": recommendation,
            "educational_notice": (
                "This analysis is educational decision support and does not guarantee outcomes or provide certain financial advice."
            ),
            "rationale": rationale,
            "risk_reward": {
                "risk": risk_score,
                "reward_proxy": reward_proxy,
                "gap": risk_reward_gap,
                "exceptional": exceptional_risk_reward,
            },
        }

    def _normalize_scores(self, submitted: Any) -> dict[str, int]:
        if not isinstance(submitted, dict):
            submitted = {}

        normalized: dict[str, int] = {}
        for metric in INVESTMENT_METRICS:
            if metric in submitted:
                normalized[metric] = int(round(_clamp_0_100(submitted.get(metric))))
            else:
                normalized[metric] = 50
        return normalized

    def _recommendation(
        self,
        *,
        average_score: float,
        confidence: float,
        risk_score: int,
        exceptional_risk_reward: bool,
    ) -> str:
        if confidence < 80 and not exceptional_risk_reward:
            return "Monitor"

        if confidence < 80 and exceptional_risk_reward:
            if average_score >= 75 and risk_score <= 55:
                return "Buy"
            return "Hold"

        if average_score >= 78 and confidence >= 85 and risk_score <= 55:
            return "Buy"
        if average_score >= 62 and confidence >= 80 and risk_score <= 70:
            return "Hold"
        if average_score < 45 or risk_score >= 82:
            return "Avoid"
        return "Monitor"


def _clamp_0_100(value: Any) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return 50.0
    return max(0.0, min(100.0, numeric))
