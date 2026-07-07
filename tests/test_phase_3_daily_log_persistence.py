from fastapi.testclient import TestClient

from backend.main import app
from backend import mission_control_service as service


client = TestClient(app)


def test_daily_log_record_health_entry():
    entry = service.record_daily_driver_log_entry("health")

    assert entry["status"] == "ok"
    assert entry["workflow"] == "health"
    assert "created_at" in entry
    assert "payload" in entry


def test_daily_log_record_start_and_end_entries():
    start = service.record_daily_driver_log_entry("start_my_day")
    end = service.record_daily_driver_log_entry("end_my_day")

    assert start["workflow"] == "start_my_day"
    assert end["workflow"] == "end_my_day"


def test_daily_log_state_shape():
    state = service.get_daily_driver_log_state(limit=5)

    assert state["status"] == "ok"
    assert state["log_type"] == "daily_driver"
    assert "counts" in state
    assert "entries" in state
    assert state["counts"]["returned"] <= 5


def test_daily_log_api_state():
    response = client.get("/api/mission-control/daily-driver-logs", params={"limit": 5})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "entries" in data


def test_daily_log_api_record():
    response = client.post(
        "/api/mission-control/daily-driver-logs/record",
        params={"workflow": "health"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["workflow"] == "health"


def test_daily_log_script_importable():
    import scripts.salus_log as salus_log

    assert callable(salus_log.main)
    assert callable(salus_log.run_record)
    assert callable(salus_log.run_recent)
    assert callable(salus_log.run_state)
