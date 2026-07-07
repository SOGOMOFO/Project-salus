from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_mission_control_v1_loads():
    response = client.get("/mission-control/v1", headers={"x-salus-token": "salus-local-token"})
    assert response.status_code == 200
    assert "Mission Control v1" in response.text
    assert "Today Mission Queue" in response.text
    assert "Quick Actions" in response.text
    assert "Generate Commander Brief" in response.text
    assert "Morning Brief" in response.text
    assert "Evening AAR" in response.text
    assert "Create Mission" in response.text
    assert "Submit SITREP" in response.text
    assert "Capture AAR" in response.text


def test_mission_control_v1_links_to_print_export():
    response = client.get("/mission-control/v1", headers={"x-salus-token": "salus-local-token"})
    assert response.status_code == 200
    assert "/mission-control/brief/latest" in response.text
    assert "Print / Export Latest Brief" in response.text
