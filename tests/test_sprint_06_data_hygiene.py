
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_06_dev_reset_requires_confirmation():
    response = client.post("/api/dev/reset", json={})
    assert response.status_code == 400


def test_sprint_06_dev_reset_clears_runtime_data():
    mission_response = client.post(
        "/missions",
        json={
            "title": "Sprint 06 Reset Test Mission",
            "intent": "Verify reset clears mission data.",
            "priority": "high",
            "status": "planned",
            "risk": "low",
            "next_action": "Run reset",
        },
    )
    assert mission_response.status_code == 200

    reset_response = client.post(
        "/api/dev/reset",
        json={"confirmation": "RESET_PROJECT_SALUS_DEV_DATA"},
    )

    assert reset_response.status_code == 200
    reset_data = reset_response.json()
    assert reset_data["status"] == "ok"
    assert reset_data["reset"] is True

    dashboard_response = client.get("/api/dashboard")
    assert dashboard_response.status_code == 200
    dashboard = dashboard_response.json()
    assert dashboard["missions_summary"]["total"] == 0

    missions_response = client.get("/api/missions")
    assert missions_response.status_code == 200
    missions = missions_response.json()
    assert missions["status"] == "ok"
    assert missions["count"] == 0
    assert missions["missions"] == []
