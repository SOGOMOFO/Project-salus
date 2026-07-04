
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


RESET_PAYLOAD = {"confirmation": "RESET_PROJECT_SALUS_DEV_DATA"}


def test_sprint_07_daily_command_page_loads():
    response = client.get("/command/daily")

    assert response.status_code == 200
    assert "Real Daily Use Mode" in response.text
    assert "Morning Commander Brief" in response.text
    assert "Evening AAR" in response.text


def test_sprint_07_real_daily_use_flow():
    reset_response = client.post("/api/dev/reset", json=RESET_PAYLOAD)
    assert reset_response.status_code == 200

    brief_response = client.post(
        "/api/daily-use/brief",
        json={
            "commander_intent": "Run Project Salus for real daily use.",
            "top_priorities": ["Brief", "Mission", "AAR"],
            "risks": ["Skipping the daily loop"],
            "next_actions": ["Create one real mission"],
        },
    )

    assert brief_response.status_code == 200
    assert brief_response.json()["status"] == "ok"

    mission_response = client.post(
        "/missions",
        json={
            "title": "Run Real Daily Use Mode",
            "intent": "Prove Kyle can use Salus for today's command loop.",
            "priority": "high",
            "status": "in_progress",
            "risk": "low",
            "next_action": "Open /command/daily",
        },
    )

    assert mission_response.status_code == 200

    aar_response = client.post(
        "/api/daily-use/aar",
        json={
            "what_happened": "Sprint 07 daily-use flow was tested.",
            "what_worked": "Brief, mission, and AAR endpoints responded.",
            "what_failed": "",
            "lesson_learned": "Daily-use mode needs to stay simple.",
            "adjustment": "Keep the dashboard focused.",
        },
    )

    assert aar_response.status_code == 200
    assert aar_response.json()["status"] == "ok"

    state_response = client.get("/api/daily-use/state")

    assert state_response.status_code == 200
    state = state_response.json()

    assert state["status"] == "ok"
    assert state["mode"] == "real_daily_use"
    assert state["missions_summary"]["total"] == 1
    assert state["aar_count"] >= 1
    assert state["daily_brief"]["commander_intent"] == "Run Project Salus for real daily use."
