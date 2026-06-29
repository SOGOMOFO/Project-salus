import asyncio
import unittest

from backend.directorates.investor_intelligence.models import (
    RECOMMENDATION_STATUSES,
    SCORE_FIELDS,
)
from backend.main import (
    investor_intelligence_status,
    investor_intelligence_framework,
    investor_intelligence_analyze,
)


class DummyRequest:
    def __init__(self, payload):
        self._payload = payload

    async def json(self):
        return self._payload


class InvestorIntelligenceTests(unittest.TestCase):
    def test_status_endpoint(self):
        payload = asyncio.run(investor_intelligence_status())
        self.assertEqual(payload["status"], "operational")
        self.assertEqual(payload["brokerage_connections"], "disabled")

    def test_framework_endpoint(self):
        payload = asyncio.run(investor_intelligence_framework())
        self.assertIn("expert_panel", payload)
        self.assertEqual(len(payload["ai_investment_categories"]), 10)
        self.assertIn("portfolio_health_placeholder", payload)

    def test_analyze_endpoint_structure_and_disclaimer(self):
        payload = asyncio.run(
            investor_intelligence_analyze(
                DummyRequest(
                    {
                        "ticker_or_asset": "NVDA",
                        "thesis": "AI infrastructure demand remains strong.",
                        "bear_case": "Capex cycle may cool faster than expected.",
                        "bull_case": "Inference demand expands margin profile.",
                        "key_assumptions": ["Demand persists", "Execution stays strong"],
                        "evidence_quality": "B",
                        "scores": {
                            "valuation": 62,
                            "financial_strength": 86,
                            "growth": 92,
                            "competitive_moat": 90,
                            "management": 88,
                            "macro_environment": 66,
                            "technical_trend": 77,
                            "risk": 58,
                            "conviction": 85,
                        },
                    }
                ),
                "salus-secure",
            )
        )

        required_fields = {
            "ticker_or_asset",
            "thesis",
            "bear_case",
            "bull_case",
            "key_assumptions",
            "evidence_quality",
            "confidence",
            "scores",
            "risks",
            "portfolio_fit",
            "recommendation",
            "disclaimer",
        }
        self.assertTrue(required_fields.issubset(payload.keys()))
        self.assertEqual(
            payload["disclaimer"],
            "This is decision-support analysis, not personalized financial advice.",
        )
        self.assertIn(payload["recommendation"], RECOMMENDATION_STATUSES)
        self.assertEqual(set(payload["scores"].keys()), set(SCORE_FIELDS))

    def test_confidence_below_80_defaults_monitor(self):
        payload = asyncio.run(
            investor_intelligence_analyze(
                DummyRequest(
                    {
                        "ticker_or_asset": "LOWCONF",
                        "evidence_quality": "D",
                        "scores": {
                            "valuation": 75,
                            "financial_strength": 70,
                            "growth": 71,
                            "competitive_moat": 70,
                            "management": 68,
                            "macro_environment": 55,
                            "technical_trend": 52,
                            "risk": 64,
                            "conviction": 63,
                        },
                    }
                ),
                "salus-secure",
            )
        )
        self.assertEqual(payload["recommendation"], "Monitor")

    def test_no_real_brokerage_connection_required(self):
        status_payload = asyncio.run(investor_intelligence_status())
        self.assertEqual(status_payload["brokerage_connections"], "disabled")


if __name__ == "__main__":
    unittest.main()
