from backend.core.risk_engine import assess_risk
from backend.core.intelligence_core import generate_judgment
from backend.core.explainability_engine import explain_recommendation


def test_risk_engine_requires_mitigation_for_high_top_risks():
    risk = assess_risk(
        {
            "mission": 20,
            "financial": 75,
            "security": 40,
            "legal": 30,
            "operational": 80,
            "reputation": 25,
            "technical": 70,
            "schedule": 60,
            "human": 45,
            "opportunity_cost": 55,
        }
    )

    assert risk["mitigation_required"] is True
    assert risk["top_risks"][0]["category"] == "operational"


def test_generate_judgment_includes_risk_report():
    judgment = generate_judgment(
        strategic_fit=85,
        evidence_quality=80,
        roi=75,
        difficulty=45,
        timeline=70,
        risks={
            "mission": 20,
            "financial": 75,
            "security": 40,
            "legal": 30,
            "operational": 80,
            "reputation": 25,
            "technical": 70,
            "schedule": 60,
            "human": 45,
            "opportunity_cost": 55,
        },
    )

    assert "recommendation" in judgment
    assert "risk" in judgment
    assert "risk_response" in judgment
    assert judgment["risk"]["mitigation_required"] is True


def test_explainability_engine_outputs_explanation():
    judgment = generate_judgment(
        strategic_fit=85,
        evidence_quality=80,
        roi=75,
        difficulty=45,
        timeline=70,
        risks={
            "mission": 20,
            "financial": 75,
            "security": 40,
            "legal": 30,
            "operational": 80,
            "reputation": 25,
            "technical": 70,
            "schedule": 60,
            "human": 45,
            "opportunity_cost": 55,
        },
    )

    explanation = explain_recommendation(judgment)

    assert explanation["recommendation"] == judgment["recommendation"]
    assert len(explanation["explanation"]) > 0
    assert "what_would_change_the_decision" in explanation