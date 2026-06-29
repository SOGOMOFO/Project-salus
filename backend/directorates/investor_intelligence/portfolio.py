from __future__ import annotations

from typing import Any


def build_portfolio_model(portfolio_fit: str, risk_score: int, conviction: int) -> dict[str, Any]:
    sizing = "small"
    if conviction >= 85 and risk_score <= 45:
        sizing = "core"
    elif conviction >= 70 and risk_score <= 60:
        sizing = "satellite"

    return {
        "fit_summary": portfolio_fit,
        "suggested_sizing": sizing,
        "risk_budget_used": round(min(1.0, max(0.0, risk_score / 100.0)), 2),
        "rebalance_trigger": "reassess if thesis changes or confidence degrades by two bands",
    }
