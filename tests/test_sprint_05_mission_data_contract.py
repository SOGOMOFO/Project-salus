from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_05_api_missions_list_contract():
    create_response = client.post(
        "/missions",
        json={
            "title": "Sprint 05 API Mission List",
            "intent": "Provide clean public mission list endpoint.",
            "priority": "high",
            "status": "planned",
            "risk": "low",
            "next_action": "Verify /api/missions",
            "due_date": "2026-07-31",
        },
    )

    assert create_response.status_code == 200

    list_response = client.get("/api/missions")

    assert list_response.status_code == 200

    data = list_response.json()

    assert data["status"] == "ok"
    assert "missions" in data
    assert "count" in data
    assert isinstance(data["missions"], list)
    assert data["count"] == len(data["missions"])


def test_sprint_05_dashboard_aar_count_reflects_created_aars():
    before_response = client.get("/api/dashboard")

    assert before_response.status_code == 200

    before_count = before_response.json()["aar_count"]

    create_response = client.post(
        "/api/aar",
        json={
            "mission": "Sprint 05 AAR Count",
            "what_happened": "Created AAR to verify dashboard count.",
            "what_worked": "AAR endpoint returned status ok.",
            "what_failed": "Dashboard count previously stayed zero.",
            "lesson_learned": "Dashboard must reflect persisted operating data.",
            "next_action": "Patch dashboard count.",
        },
    )

    assert create_response.status_code == 200
    assert create_response.json()["status"] == "ok"

    after_response = client.get("/api/dashboard")

    assert after_response.status_code == 200

    after_count = after_response.json()["aar_count"]

    assert after_count >= before_count + 1
