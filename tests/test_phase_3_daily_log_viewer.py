from fastapi.testclient import TestClient

from backend.main import app
from backend import mission_control_service as service


client = TestClient(app)


def test_daily_history_records_seed_entries():
    service.record_daily_driver_log_entry("health")
    service.record_daily_driver_log_entry("start_my_day")
    service.record_daily_driver_log_entry("end_my_day")

    state = service.get_daily_driver_history_view(limit=10)

    assert state["status"] == "ok"
    assert state["view"] == "daily_driver_history"
    assert len(state["entries"]) >= 3
    assert "last_start" in state
    assert "last_end" in state
    assert "last_health" in state


def test_last_daily_driver_log_entry():
    service.record_daily_driver_log_entry("start_my_day")

    state = service.get_last_daily_driver_log_entry("start_my_day")

    assert state["status"] == "ok"
    assert state["found"] is True
    assert state["entry"]["workflow"] == "start_my_day"


def test_last_aar_summary_shape():
    service.record_daily_driver_log_entry("end_my_day")

    state = service.get_last_end_my_day_aar_summary()

    assert state["status"] == "ok"
    assert state["found"] is True
    assert state["view"] == "last_end_my_day_aar_summary"
    assert "summary" in state
    assert "tomorrow_setup" in state


def test_daily_history_api():
    service.record_daily_driver_log_entry("health")

    response = client.get("/api/mission-control/daily-driver-history", params={"limit": 5})

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["view"] == "daily_driver_history"


def test_last_aar_api():
    service.record_daily_driver_log_entry("end_my_day")

    response = client.get("/api/mission-control/daily-driver-history/last-aar")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "found" in data


def test_daily_history_script_importable():
    import scripts.salus_history as salus_history

    assert callable(salus_history.main)
    assert callable(salus_history.run_recent)
    assert callable(salus_history.run_last)
    assert callable(salus_history.run_last_aar)
