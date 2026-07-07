from fastapi.testclient import TestClient

from backend.main import app
from backend import mission_control_service as service


client = TestClient(app)


def test_start_my_day_service_shape():
    state = service.get_start_my_day_workflow_state()

    assert state["status"] == "ok"
    assert state["workflow"] == "start_my_day"
    assert "commander_intent" in state
    assert len(state["top_actions"]) == 3
    assert len(state["top_risks"]) >= 1
    assert "end_of_day_aar_prompt" in state


def test_start_my_day_contains_health_and_connector_posture():
    state = service.get_start_my_day_workflow_state()

    assert "health_summary" in state
    assert "connector_posture" in state
    assert "counts" in state["health_summary"]
    assert "counts" in state["connector_posture"]


def test_start_my_day_api():
    response = client.get("/api/mission-control/start-my-day")

    assert response.status_code == 200
    data = response.json()
    assert data["workflow"] == "start_my_day"
    assert len(data["top_actions"]) == 3


def test_start_my_day_script_importable():
    import scripts.start_my_day as start_my_day

    assert callable(start_my_day.main)
