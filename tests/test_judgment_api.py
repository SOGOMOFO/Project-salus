from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_judgment_api_returns_judgment_and_explanation():
    response = client.post(
        "/api/judgment",
        json={
            "strategic_fit": 85,
            "evidence_quality": 80,
            "roi": 75,
            "difficulty": 45,
            "timeline": 70,
            "risks": {
                "mission": 20,
                "financial": 75,
                "security": 40,
                "legal": 30,
                "operational": 80,
                "reputation": 25,
                "technical": 70,
                "schedule": 60,
                "human": 45,
                "opportunity_cost": 55
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "judgment" in data
    assert "explanation" in data
    assert data["judgment"]["risk"]["mitigation_required"] is True
