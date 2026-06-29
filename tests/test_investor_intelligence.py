import asyncio
import unittest

from backend.directorates.investor_intelligence import (
    INVESTMENT_METRICS,
    RECOMMENDATION_STATUSES,
    DIRECTORATE,
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
    def test_framework_contract(self):
        framework = DIRECTORATE.framework()
        self.assertEqual(framework["directorate"], "Investor Intelligence Directorate")
        self.assertEqual(framework["scoring_model"]["metrics"], INVESTMENT_METRICS)
        self.assertEqual(framework["recommendation_statuses"], RECOMMENDATION_STATUSES)

    def test_default_monitor_when_low_confidence(self):
        payload = DIRECTORATE.analyze(
            {
                "ticker": "TEST",
                "confidence": 74,
                "scores": {
                    "valuation": 85,
                    "financial_strength": 85,
                    "growth": 82,
                    "moat": 86,
                    "management": 84,
                    "macro": 70,
                    "technical": 72,
                    "risk": 69,
                    "conviction": 78,
                },
            }
        )
        self.assertEqual(payload["recommendation"], "Monitor")
        self.assertIn("educational", payload["educational_notice"].lower())

    def test_can_escape_monitor_on_exceptional_risk_reward(self):
        payload = DIRECTORATE.analyze(
            {
                "ticker": "EXC",
                "confidence": 70,
                "scores": {
                    "valuation": 88,
                    "financial_strength": 91,
                    "growth": 92,
                    "moat": 93,
                    "management": 89,
                    "macro": 80,
                    "technical": 85,
                    "risk": 30,
                    "conviction": 90,
                },
            }
        )
        self.assertNotEqual(payload["recommendation"], "Monitor")
        self.assertTrue(payload["risk_reward"]["exceptional"])

    def test_api_endpoints(self):
        status_payload = asyncio.run(investor_intelligence_status())
        self.assertEqual(status_payload["status"], "operational")

        framework_payload = asyncio.run(investor_intelligence_framework())
        self.assertEqual(framework_payload["recommendation_statuses"], RECOMMENDATION_STATUSES)

        analyze_payload = asyncio.run(
            investor_intelligence_analyze(
                DummyRequest(
                    {
                        "ticker": "API",
                        "confidence": 82,
                        "scores": {
                            "valuation": 70,
                            "financial_strength": 78,
                            "growth": 76,
                            "moat": 74,
                            "management": 72,
                            "macro": 67,
                            "technical": 66,
                            "risk": 58,
                            "conviction": 79,
                        },
                    }
                )
            )
        )
        self.assertIn(analyze_payload["recommendation"], RECOMMENDATION_STATUSES)
        self.assertEqual(analyze_payload["ticker"], "API")


if __name__ == "__main__":
    unittest.main()
