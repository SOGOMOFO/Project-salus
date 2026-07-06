from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_mission_control_has_navigation_shell():
    response = client.get("/mission-control/ui")
    assert response.status_code == 200
    assert "Command Home" in response.text
    assert "/command-home" in response.text
    assert "Command OS" in response.text
    assert "/command" in response.text
    assert "Daily Driver" in response.text
    assert "/docs" in response.text
