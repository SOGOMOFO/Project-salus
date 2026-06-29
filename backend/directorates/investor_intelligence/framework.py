from __future__ import annotations

from backend.directorates.investor_intelligence.agent import panel_names
from backend.directorates.investor_intelligence.models import (
    CONFIDENCE_BANDS,
    EVIDENCE_QUALITY_GRADES,
    RECOMMENDATION_STATUSES,
    SCORE_FIELDS,
)
from backend.directorates.investor_intelligence.scenarios import SCENARIO_PLACEHOLDERS


AI_INVESTMENT_CATEGORIES = [
    "infrastructure",
    "foundation_models",
    "enterprise_ai_software",
    "robotics",
    "cybersecurity",
    "healthcare_ai",
    "defense_ai",
    "industrial_automation",
    "edge_ai",
    "ai_enabled_services",
]

PORTFOLIO_HEALTH_PLACEHOLDER = {
    "cash_allocation": "placeholder",
    "equity_allocation": "placeholder",
    "crypto_allocation": "placeholder",
    "bonds": "placeholder",
    "precious_metals": "placeholder",
    "private_investments": "placeholder",
    "real_estate": "placeholder",
    "business_ownership": "placeholder",
    "emergency_liquidity": "placeholder",
    "debt": "placeholder",
    "tax_exposure": "placeholder",
}


def get_framework() -> dict:
    return {
        "mission": "Deliver disciplined, educational investment decision support under uncertainty.",
        "doctrine": [
            "Evidence first, narrative second.",
            "Protect downside before pursuing upside.",
            "Use confidence thresholds to enforce decision discipline.",
        ],
        "pipeline": [
            "Ingest thesis and assumptions",
            "Score across 9-factor model",
            "Run expert panel interpretation",
            "Apply confidence and risk/reward policy",
            "Produce recommendation with disclaimer",
        ],
        "expert_panel": panel_names(),
        "scoring_model": {
            "scores": SCORE_FIELDS,
            "range": "0-100",
            "evidence_quality": EVIDENCE_QUALITY_GRADES,
            "confidence_bands": CONFIDENCE_BANDS,
        },
        "recommendation_statuses": RECOMMENDATION_STATUSES,
        "ai_investment_categories": AI_INVESTMENT_CATEGORIES,
        "portfolio_health_placeholder": PORTFOLIO_HEALTH_PLACEHOLDER,
        "scenario_placeholders": SCENARIO_PLACEHOLDERS,
        "constraints": {
            "brokerage_connections": "disabled",
            "decision_support_only": True,
        },
    }
