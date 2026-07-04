
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_02_command_ui_returns_html():
    response = client.get("/command")

    assert response.status_code == 200
    assert "Salus Command OS" in response.text
    assert "/api/dashboard" in response.text
    assert "/api/daily-brief" in response.text


def test_sprint_02_core_missions_lists_created_mission():
    create_response = client.post(
        "/missions",
        json={
            "title": "Sprint 02 UI Smoke Test",
            "intent": "Verify UI mission list support.",
            "priority": "high",
            "status": "planned",
            "risk": "low",
            "next_action": "Load command page",
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()["mission"]

    list_response = client.get("/api/core/missions")

    assert list_response.status_code == 200
    missions = list_response.json()["missions"]

    assert any(mission["id"] == created["id"] for mission in missions)
