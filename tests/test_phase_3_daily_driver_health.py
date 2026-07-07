from fastapi.testclient import TestClient

from backend.main import app
from backend import mission_control_service as service


client = TestClient(app)


def test_daily_driver_health_service_shape():
    state = service.get_daily_driver_health_state()

    assert state["status"] in {"ready", "usable_with_warnings", "not_ready"}
    assert "daily_use_ready" in state
    assert state["counts"]["components"] >= 4
    assert "components" in state
    assert "recommended_action" in state


def test_daily_driver_health_has_database_component():
    state = service.get_daily_driver_health_state()
    names = {item["name"] for item in state["components"]}

    assert "database" in names
    assert "mission_control" in names


def test_daily_driver_health_api():
    response = client.get("/api/mission-control/daily-driver-health")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"ready", "usable_with_warnings", "not_ready"}
    assert "components" in data
    assert "recommended_action" in data


def test_daily_driver_script_importable():
    import scripts.daily_driver_check as check

    assert callable(check.main)
