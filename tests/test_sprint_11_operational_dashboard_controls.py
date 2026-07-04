
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_11_operational_dashboard_page_loads():
    response = client.get("/command/ops")

    assert response.status_code == 200
    assert "Operational Dashboard" in response.text
    assert "Daily Brief" in response.text
    assert "Mission" in response.text
    assert "Schoolhouse Course" in response.text
    assert "Schoolhouse Study Session" in response.text
    assert "Charisma Self-Assessment" in response.text
    assert "Charisma Conversation AAR" in response.text


def test_sprint_11_operational_dashboard_supports_existing_state_endpoint():
    response = client.get("/api/command/integrated-state")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert "daily_use" in data
    assert "schoolhouse" in data
    assert "charisma" in data
