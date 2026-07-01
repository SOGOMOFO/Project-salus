from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_commander_brief_endpoint_returns_readable_brief():
    response = client.get("/api/commander/brief")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "brief" in data
    assert "data" in data
    assert "PROJECT SALUS COMMANDER BRIEF" in data["brief"]
    assert "Operating Status: ACTIVE" in data["brief"]
    assert "Next Recommended Action:" in data["brief"]
    assert data["data"]["operating_status"] == "active"


def test_commander_next_action_endpoint_returns_action():
    response = client.get("/api/commander/next-action")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "next_recommended_action" in data
    assert "blocked_missions" in data
    assert "high_priority_open" in data
    assert isinstance(data["blocked_missions"], list)
    assert isinstance(data["high_priority_open"], list)


def test_dashboard_summary_endpoint_returns_counts():
    response = client.get("/api/dashboard/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "dashboard" in data
    assert data["dashboard"]["operating_status"] == "active"
    assert "counts" in data["dashboard"]
    assert "next_recommended_action" in data["dashboard"]
    assert "open_missions" in data["dashboard"]["counts"]
    assert "blocked_missions" in data["dashboard"]["counts"]
