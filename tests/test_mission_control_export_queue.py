from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_latest_brief_print_view_loads():
    client.post("/mission-control/commander-brief", follow_redirects=False)

    response = client.get("/mission-control/brief/latest")

    assert response.status_code == 200
    assert "Print / Save PDF" in response.text
    assert "Back to Mission Control" in response.text


def test_mission_control_ui_contains_export_and_queue():
    response = client.get("/mission-control/ui", headers={"x-salus-token": "salus-local-token"})

    assert response.status_code == 200
    assert "Today Mission Queue" in response.text
    assert "Print / Export Latest Brief" in response.text
    assert "/mission-control/brief/latest" in response.text
