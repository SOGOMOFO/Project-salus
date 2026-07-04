
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_13_review_state_endpoint():
    response = client.get("/api/command/review-state")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["module"] == "operational_review_history"
    assert "counts" in data
    assert "data" in data
    assert "missions" in data["data"]
    assert "schoolhouse_courses" in data["data"]
    assert "charisma_self_assessments" in data["data"]


def test_sprint_13_review_dashboard_page_loads():
    response = client.get("/command/review")

    assert response.status_code == 200
    assert "Operational Review Dashboard" in response.text
    assert "Daily Briefs" in response.text
    assert "Missions" in response.text
    assert "Schoolhouse Courses" in response.text
    assert "Charisma Self-Assessments" in response.text
    assert "Charisma Conversation AARs" in response.text
