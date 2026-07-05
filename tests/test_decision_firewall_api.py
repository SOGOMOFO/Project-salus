from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_decision_firewall_framework_loads():
    response = client.get("/decision-firewall/framework")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Project Salus Decision Firewall"
    assert "PURSUE" in data["recommendations"]
    assert "DISCARD" in data["recommendations"]


def test_echo_seven_ai_governance_offer_should_be_pursued():
    payload = {
        "title": "Echo Seven AI Governance & Cyber Readiness Assessment",
        "category": "venture",
        "claim": "Small businesses need help safely adopting AI tools.",
        "evidence_type": "strong_evidence",
        "strategic_fit": 10,
        "roi": 9,
        "difficulty": 5,
        "risk": 4,
        "opportunity_cost": 3,
        "actionability": 9,
        "output_type": "service_offer",
        "owner": "Echo Seven",
    }

    response = client.post("/decision-firewall/evaluate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["recommendation"] == "PURSUE"
    assert data["decision_score"] >= 75
    assert data["no_bloat_gate"]["passed"] is True


def test_unverified_ai_hidden_code_claim_should_not_be_implemented():
    payload = {
        "title": "AI Decoded Hidden Biblical Code",
        "category": "claim_analysis",
        "claim": "Grok discovered a supernatural hidden code in scripture.",
        "evidence_type": "ai_generated_pattern",
        "strategic_fit": 3,
        "roi": 2,
        "difficulty": 6,
        "risk": 8,
        "opportunity_cost": 7,
        "actionability": 2,
        "output_type": "discard",
        "owner": "Curiosity Parking Lot",
    }

    response = client.post("/decision-firewall/evaluate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["recommendation"] == "DISCARD"
    assert data["evidence"]["requires_verification"] is True
    assert data["no_bloat_gate"]["passed"] is False
