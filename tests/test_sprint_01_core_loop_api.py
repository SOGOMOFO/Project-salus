
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_01_dashboard_endpoint_returns_summary():
    response = client.get("/api/dashboard")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "operational"
    assert "missions_summary" in data
    assert "daily_brief" in data
    assert "aar_count" in data
    assert data["judgment_ready"] is True


def test_sprint_01_daily_brief_create_and_retrieve():
    payload = {
        "commander_intent": "Ship Sprint 01 Core Loop.",
        "top_priorities": ["Run tests", "Commit changes"],
        "risks": ["Scope creep"],
        "opportunities": ["Daily use validation"],
        "next_actions": ["Execute pytest"],
    }

    create_response = client.post("/api/daily-brief", json=payload)

    assert create_response.status_code == 200
    created = create_response.json()["daily_brief"]
    assert created["commander_intent"] == "Ship Sprint 01 Core Loop."

    get_response = client.get("/api/daily-brief")

    assert get_response.status_code == 200
    retrieved = get_response.json()["daily_brief"]
    assert retrieved["commander_intent"] == "Ship Sprint 01 Core Loop."


def test_sprint_01_mission_create_and_update():
    create_payload = {
        "title": "Build Sprint 01 Core Loop",
        "intent": "Make Project Salus usable daily.",
        "priority": "high",
        "status": "planned",
        "risk": "low",
        "next_action": "Create endpoint tests",
        "due_date": "2026-07-31",
    }

    create_response = client.post("/missions", json=create_payload)

    assert create_response.status_code == 200
    created = create_response.json()["mission"]
    assert created["title"] == "Build Sprint 01 Core Loop"

    mission_id = created["id"]

    update_response = client.patch(
        f"/missions/{mission_id}",
        json={
            "status": "in_progress",
            "next_action": "Run pytest",
            "risk": "medium",
        },
    )

    assert update_response.status_code == 200
    updated = update_response.json()["mission"]

    assert updated["id"] == mission_id
    assert updated["status"] == "in_progress"
    assert updated["next_action"] == "Run pytest"
    assert updated["risk"] == "medium"
