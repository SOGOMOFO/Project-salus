
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_19_readiness_endpoint():
    response = client.get("/api/command/readiness")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["module"] == "system_status_readiness_scoring"
    assert "score" in data
    assert "max_score" in data
    assert data["max_score"] == 100
    assert "readiness_level" in data
    assert "components" in data
    assert "system" in data["components"]
    assert "daily_operations" in data["components"]
    assert "schoolhouse" in data["components"]
    assert "charisma" in data["components"]
    assert "data_hygiene" in data["components"]
    assert data["primary_pages"]["workflows"] == "/command/workflows"


def test_sprint_19_readiness_page_loads():
    response = client.get("/command/readiness")

    assert response.status_code == 200
    assert "Project Salus — Readiness" in response.text
    assert "Overall Readiness" in response.text
    assert "Daily Operations" in response.text
    assert "Schoolhouse" in response.text
    assert "Charisma" in response.text
    assert "Data Hygiene" in response.text
    assert "/api/command/readiness" in response.text
