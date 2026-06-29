import unittest

from backend.directorates.investor_intelligence.portfolio import build_portfolio_model
from backend.directorates.investor_intelligence.recommendation import build_recommendation
from backend.directorates.investor_intelligence.scenarios import run_scenarios


class InvestorAlphaTests(unittest.TestCase):
    def test_scenario_engine_output_shape(self):
        payload = run_scenarios({"risk": 62, "growth": 81, "macro_environment": 47})
        self.assertIn("recession", payload)
        self.assertIn("ai_adoption_acceleration", payload)

    def test_portfolio_model_structure(self):
        model = build_portfolio_model("Core candidate", risk_score=40, conviction=90)
        self.assertEqual(model["suggested_sizing"], "core")
        self.assertIn("risk_budget_used", model)

    def test_recommendation_engine(self):
        recommendation = build_recommendation(
            composite_score=83,
            confidence_band=90,
            exceptional_risk_reward=True,
            risk_score=45,
        )
        self.assertIn(recommendation, {"Buy", "Hold", "Monitor", "Avoid"})


if __name__ == "__main__":
    unittest.main()
