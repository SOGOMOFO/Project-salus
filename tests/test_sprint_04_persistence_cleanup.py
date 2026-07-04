
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_04_mission_persistence_file_created_after_create_and_update():
    create_response = client.post(
        "/api/missions",
        json={
            "title": "Sprint 04 Persistent Mission",
            "intent": "Verify mission persistence.",
            "priority": "high",
            "status": "planned",
            "risk": "medium",
            "next_action": "Create persistence file",
        },
    )

    assert create_response.status_code == 200
    mission = create_response.json()["mission"]
    mission_id = mission["id"]

    update_response = client.patch(
        f"/api/missions/{mission_id}",
        json={
            "status": "completed",
            "risk": "low",
            "next_action": "Persistence verified",
        },
    )

    assert update_response.status_code == 200

    missions_file = Path("data/salus_missions.json")
    assert missions_file.exists()

    contents = missions_file.read_text()
    assert mission_id in contents
    assert "Persistence verified" in contents


def test_sprint_04_daily_brief_persistence_file_created():
    response = client.post(
        "/api/daily-brief",
        json={
            "commander_intent": "Persist Sprint 04 daily brief.",
            "top_priorities": ["Persistence"],
            "risks": ["Data loss"],
            "next_actions": ["Run tests"],
        },
    )

    assert response.status_code == 200

    brief_file = Path("data/salus_daily_briefs.json")
    assert brief_file.exists()
    assert "Persist Sprint 04 daily brief." in brief_file.read_text()


def test_sprint_04_aar_persistence_file_created():
    response = client.post(
        "/api/aar",
        json={
            "what_happened": "Sprint 04 added local JSON persistence.",
            "what_worked": "Batch execution.",
            "what_failed": "Nothing material.",
            "lesson_learned": "Persist early.",
            "adjustment": "Keep local-first storage until database is justified.",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "aar_id" in data
    assert data["aar"]["what_happened"] == "Sprint 04 added local JSON persistence."

    aar_file = Path("data/salus_aars.json")
    assert aar_file.exists()
    assert "Sprint 04 added local JSON persistence." in aar_file.read_text()


def test_sprint_04_command_ui_still_loads():
    response = client.get("/command")

    assert response.status_code == 200
    assert "Salus Command OS" in response.text
    assert "AAR Entry" in response.text
    assert "Create Mission" in response.text
