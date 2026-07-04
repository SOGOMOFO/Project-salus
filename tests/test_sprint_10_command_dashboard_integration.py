
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_10_integrated_command_state():
    response = client.get("/api/command/integrated-state")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["module"] == "command_dashboard_integration"
    assert "daily_use" in data
    assert "schoolhouse" in data
    assert "charisma" in data
    assert "next_actions" in data


def test_sprint_10_integrated_command_dashboard_page():
    response = client.get("/command/integrated")

    assert response.status_code == 200
    assert "Integrated Command Dashboard" in response.text
    assert "Schoolhouse" in response.text
    assert "Charisma" in response.text
    assert "Daily Use" in response.text
