
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_14_command_health_endpoint():
    response = client.get("/api/command/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["module"] == "command_launcher_navigation"
    assert data["system"] == "Project Salus Mission Control"
    assert data["primary_pages"]["ops_dashboard"] == "/command/ops"
    assert data["primary_pages"]["review_dashboard"] == "/command/review"


def test_sprint_14_home_page_loads():
    response = client.get("/")

    assert response.status_code == 200
    assert "<html" in response.text.lower()


def test_sprint_14_command_home_is_launcher():
    response = client.get("/command/home")

    assert response.status_code == 200
    assert "Project Salus Mission Control" in response.text
    assert "Open Operational Dashboard" in response.text
    assert "/command/review" in response.text
    assert "/api/command/health" in response.text


def test_sprint_14_command_home_page_loads():
    response = client.get("/command/home")

    assert response.status_code == 200
    assert "Project Salus Mission Control" in response.text
    assert "Schoolhouse" in response.text
    assert "Charisma" in response.text


def test_sprint_14_start_stop_scripts_exist():
    start_script = Path("scripts/start_salus.sh")
    stop_script = Path("scripts/stop_salus.sh")

    assert start_script.exists()
    assert stop_script.exists()

    assert "uvicorn backend.main:app" in start_script.read_text()
    assert "lsof -ti:8000" in stop_script.read_text()
