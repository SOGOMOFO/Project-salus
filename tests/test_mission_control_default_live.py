from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_mission_control_default_redirects_to_v1():
    response = client.get("/mission-control", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/mission-control/v1"


def test_mission_control_live_status_returns_counts():
    response = client.get("/api/mission-control/live-status")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "active_missions" in data
    assert "blocked_missions" in data
    assert "total_missions" in data


def test_mission_control_v1_contains_live_status_script():
    response = client.get("/mission-control/v1")
    assert response.status_code == 200
    assert "live-status" in response.text
    assert "/api/mission-control/live-status" in response.text
    assert "setInterval" in response.text
