from fastapi.testclient import TestClient

from backend.main import app
from backend import mission_control_service as service


client = TestClient(app)


def test_end_my_day_service_shape():
    state = service.get_end_my_day_workflow_state()

    assert state["status"] == "ok"
    assert state["workflow"] == "end_my_day"
    assert state["aar_type"] == "daily_closeout"
    assert len(state["aar_questions"]) >= 5
    assert "carry_forward_candidates" in state
    assert "tomorrow_setup" in state


def test_end_my_day_builds_aar_entry():
    entry = service.build_end_my_day_aar_entry(
        moved_forward="Finished Project Salus block.",
        blocked="No major blocker.",
        improve_tomorrow="Start earlier.",
        remember_or_track="Track daily use readiness.",
        highest_value_action="Run Start My Day.",
    )

    assert entry["status"] == "ok"
    assert entry["workflow"] == "end_my_day"
    assert entry["tomorrow_first_action"] == "Run Start My Day."


def test_end_my_day_api():
    response = client.get("/api/mission-control/end-my-day")

    assert response.status_code == 200
    data = response.json()
    assert data["workflow"] == "end_my_day"
    assert len(data["aar_questions"]) >= 5


def test_end_my_day_aar_api():
    response = client.post(
        "/api/mission-control/end-my-day/aar",
        params={
            "moved_forward": "Moved Project Salus forward.",
            "blocked": "Nothing major.",
            "improve_tomorrow": "Use Start My Day first.",
            "remember_or_track": "Track daily-driver stability.",
            "highest_value_action": "Open Mission Control.",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["workflow"] == "end_my_day"
    assert data["tomorrow_first_action"] == "Open Mission Control."


def test_end_my_day_script_importable():
    import scripts.end_my_day as end_my_day

    assert callable(end_my_day.main)
