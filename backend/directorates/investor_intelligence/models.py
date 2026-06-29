from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator


SCORE_FIELDS = [
    "valuation",
    "financial_strength",
    "growth",
    "competitive_moat",
    "management",
    "macro_environment",
    "technical_trend",
    "risk",
    "conviction",
]

EVIDENCE_QUALITY_GRADES = ["A+", "A", "B", "C", "D"]
CONFIDENCE_BANDS = [99, 95, 90, 80, 70, 60, "below_60"]
RECOMMENDATION_STATUSES = ["Buy", "Hold", "Monitor", "Avoid"]


class ScoreCard(BaseModel):
    valuation: int = Field(default=50)
    financial_strength: int = Field(default=50)
    growth: int = Field(default=50)
    competitive_moat: int = Field(default=50)
    management: int = Field(default=50)
    macro_environment: int = Field(default=50)
    technical_trend: int = Field(default=50)
    risk: int = Field(default=50)
    conviction: int = Field(default=50)

    @field_validator("*")
    @classmethod
    def clamp_scores(cls, value: int) -> int:
        return max(0, min(100, int(value)))


class AnalyzeRequest(BaseModel):
    ticker_or_asset: str = Field(default="UNKNOWN")
    thesis: str = Field(default="")
    bear_case: str = Field(default="")
    bull_case: str = Field(default="")
    key_assumptions: list[str] = Field(default_factory=list)
    evidence_quality: Literal["A+", "A", "B", "C", "D"] = "C"
    scores: ScoreCard = Field(default_factory=ScoreCard)
    risks: list[str] = Field(default_factory=list)
    portfolio_fit: str = Field(default="Satellite allocation candidate pending portfolio context.")


class AnalyzeResponse(BaseModel):
    ticker_or_asset: str
    thesis: str
    bear_case: str
    bull_case: str
    key_assumptions: list[str]
    evidence_quality: str
    confidence: int | str
    scores: dict[str, int]
    risks: list[str]
    portfolio_fit: str
    recommendation: Literal["Buy", "Hold", "Monitor", "Avoid"]
    disclaimer: str
    risk_reward: dict[str, float | bool]
    panel_summary: list[dict[str, str]]
    scenario_outlook: dict[str, str]
    portfolio_model: dict[str, str | float]
