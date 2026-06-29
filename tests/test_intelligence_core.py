import asyncio
import unittest

from backend.core.intelligence_api import intelligence_status, intelligence_evaluate, intelligence_reconcile
from backend.core.intelligence_core import (
    evaluate_decision,
    generate_recommendation,
    reconcile_agent_outputs,
    score_evidence,
)


class DummyRequest:
    def __init__(self, payload):
        self._payload = payload

    async def json(self):
        return self._payload


class IntelligenceCoreTests(unittest.TestCase):
    def test_status_endpoint(self):
        payload = asyncio.run(
            intelligence_status(
                x_salus_passphrase="salus-secure",
                x_salus_token=None,
                x_salus_role="readonly",
            )
        )
        self.assertEqual(payload["status"], "ok")
        self.assertIn("evaluate_decision", payload["capabilities"])

    def test_decision_evaluation(self):
        payload = evaluate_decision(
            {
                "topic": "expand directorate",
                "strategic_fit": 90,
                "evidence_quality": 86,
                "roi": 82,
                "difficulty": 35,
                "risk": 30,
                "opportunity_cost": 28,
                "timeline": 78,
                "evidence": {"credibility": 90, "coverage": 85, "freshness": 80, "consistency": 88},
            },
            memory_writer=lambda _record: None,
            audit_logger=lambda _record: None,
        )
        self.assertIn("decision_scoring", payload)
        self.assertIn(payload["overall"]["recommendation"], {"Pursue", "Pause", "Delegate", "Discard", "Monitor"})

    def test_evidence_scoring(self):
        high = score_evidence({"credibility": 98, "coverage": 96, "freshness": 95, "consistency": 97})
        low = score_evidence({"credibility": 45, "coverage": 40, "freshness": 35, "consistency": 30})
        self.assertIn(high["grade"], {"A+", "A", "B", "C", "D"})
        self.assertIn(low["grade"], {"A+", "A", "B", "C", "D"})
        self.assertGreater(high["score"], low["score"])

    def test_recommendation_generation(self):
        recommendation = generate_recommendation(
            strategic_fit=88,
            evidence_quality=90,
            roi=85,
            difficulty=30,
            risk=25,
            opportunity_cost=20,
            timeline=80,
        )
        self.assertIn(recommendation["recommendation"], {"Pursue", "Pause", "Delegate", "Discard", "Monitor"})
        self.assertIn(recommendation["confidence"], {99, 95, 90, 80, 70, 60, "below_60"})

    def test_agent_output_reconciliation(self):
        result = reconcile_agent_outputs(
            [
                {"agent": "alpha", "recommendation": "Pursue", "confidence": 92},
                {"agent": "beta", "recommendation": "Pursue", "confidence": 88},
                {"agent": "gamma", "recommendation": "Monitor", "confidence": 70},
            ]
        )
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["consensus"], "Pursue")

    def test_memory_failure_tolerance(self):
        payload = evaluate_decision(
            {
                "topic": "risky move",
                "strategic_fit": 60,
                "evidence_quality": 55,
                "roi": 58,
                "difficulty": 70,
                "risk": 75,
                "opportunity_cost": 62,
                "timeline": 50,
                "evidence": "limited signal",
            },
            memory_writer=lambda _record: (_ for _ in ()).throw(RuntimeError("memory unavailable")),
            audit_logger=lambda _record: None,
        )
        self.assertIn("overall", payload)
        self.assertIn(payload["overall"]["confidence"], {99, 95, 90, 80, 70, 60, "below_60"})

    def test_evaluate_endpoint(self):
        payload = asyncio.run(
            intelligence_evaluate(
                request=DummyRequest(
                    {
                        "topic": "new capability",
                        "strategic_fit": 82,
                        "evidence_quality": 79,
                        "roi": 81,
                        "difficulty": 40,
                        "risk": 38,
                        "opportunity_cost": 25,
                        "timeline": 76,
                        "evidence": {"credibility": 80, "coverage": 78, "freshness": 75, "consistency": 79},
                    }
                ),
                x_salus_passphrase="salus-secure",
                x_salus_token=None,
                x_salus_role="agent",
            )
        )
        self.assertEqual(payload["status"], "ok")
        self.assertIn("decision", payload)

    def test_reconcile_endpoint(self):
        payload = asyncio.run(
            intelligence_reconcile(
                request=DummyRequest(
                    {
                        "outputs": [
                            {"agent": "planner", "recommendation": "Delegate", "confidence": 83},
                            {"agent": "risk", "recommendation": "Monitor", "confidence": 75},
                            {"agent": "ops", "recommendation": "Delegate", "confidence": 81},
                        ]
                    }
                ),
                x_salus_passphrase="salus-secure",
                x_salus_token=None,
                x_salus_role="family",
            )
        )
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["reconciliation"]["consensus"], "Delegate")


if __name__ == "__main__":
    unittest.main()
