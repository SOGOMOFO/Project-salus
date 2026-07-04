
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_17_morning_workflow_endpoint():
    response = client.get("/api/workflows/morning")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["workflow"] == "morning"
    assert data["module"] == "daily_workflow_automation"
    assert "checklist" in data
    assert len(data["checklist"]) >= 5
    assert data["first_action"] == "Open /command/daily-driver."


def test_sprint_17_evening_workflow_endpoint():
    response = client.get("/api/workflows/evening")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["workflow"] == "evening"
    assert "checklist" in data
    assert len(data["checklist"]) >= 5
    assert data["final_action"] == "Set tomorrow’s first next action."


def test_sprint_17_today_workflow_endpoint():
    response = client.get("/api/workflows/today")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["module"] == "daily_workflow_automation"
    assert "morning" in data
    assert "evening" in data
    assert data["page"] == "/command/workflows"


def test_sprint_17_workflows_page_loads():
    response = client.get("/command/workflows")

    assert response.status_code == 200
    assert "Daily Workflow Automation" in response.text
    assert "Morning Workflow" in response.text
    assert "Evening Closeout" in response.text
    assert "/command/daily-driver" in response.text
    assert "/command/records" in response.text
