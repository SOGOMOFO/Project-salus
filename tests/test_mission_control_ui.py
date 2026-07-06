from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_mission_control_ui_loads():
    response = client.get("/mission-control/ui")
    assert response.status_code == 200
    assert "Project Salus Mission Control" in response.text
    assert "Commander Priority" in response.text
    assert "Missions" in response.text
