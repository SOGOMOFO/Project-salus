
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_15_daily_driver_state_endpoint():
    response = client.get("/api/command/daily-driver-state")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["module"] == "daily_driver_polish"
    assert "morning_workflow" in data
    assert "evening_closeout" in data
    assert "callouts" in data
    assert "missions" in data["callouts"]
    assert data["primary_pages"]["ops"] == "/command/ops"


def test_sprint_15_daily_driver_page_loads():
    response = client.get("/command/daily-driver")

    assert response.status_code == 200
    assert "Project Salus — Daily Driver" in response.text
    assert "Morning Workflow" in response.text
    assert "Evening Closeout" in response.text
    assert "Mission Callout" in response.text
    assert "Schoolhouse Callout" in response.text
    assert "Charisma Drill Callout" in response.text
    assert "/command/ops" in response.text
    assert "/command/review" in response.text
