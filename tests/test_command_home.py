from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_command_home_loads():
    response = client.get("/command-home")
    assert response.status_code == 200
    assert "Project Salus Command Home" in response.text
    assert "Mission Control" in response.text
    assert "/mission-control/ui" in response.text
    assert "API Docs" in response.text
    assert "Kernel" in response.text


def test_existing_command_route_still_loads():
    response = client.get("/command")
    assert response.status_code == 200
    assert "Salus Command OS" in response.text
