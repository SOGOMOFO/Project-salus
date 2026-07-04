
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_03_command_page_contains_mission_and_aar_ui():
    response = client.get("/command")

    assert response.status_code == 200
    assert "Salus Command OS" in response.text
    assert "Create Mission" in response.text
    assert "Update Mission" in response.text
    assert "AAR Entry" in response.text
    assert "AAR Log" in response.text


def test_sprint_03_api_missions_create_list_update():
    create_response = client.post(
        "/api/missions",
        json={
            "title": "Sprint 03 Mission",
            "intent": "Test mission UI API compatibility.",
            "priority": "high",
            "status": "planned",
            "risk": "medium",
            "next_action": "Run Sprint 03 tests",
            "due_date": "2026-07-31",
        },
    )

    assert create_response.status_code == 200
    mission = create_response.json()["mission"]
    mission_id = mission["id"]

    list_response = client.get("/api/missions")

    assert list_response.status_code == 200
    missions = list_response.json()["missions"]
    assert any(item["id"] == mission_id for item in missions)

    update_response = client.patch(
        f"/api/missions/{mission_id}",
        json={
            "status": "in_progress",
            "priority": "high",
            "risk": "low",
            "next_action": "Commit Sprint 03",
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()["mission"]

    assert updated["id"] == mission_id
    assert updated["status"] == "in_progress"
    assert updated["risk"] == "low"
    assert updated["next_action"] == "Commit Sprint 03"


def test_sprint_03_dashboard_still_available():
    response = client.get("/api/dashboard")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "operational"
    assert "missions_summary" in data
    assert "daily_brief" in data
