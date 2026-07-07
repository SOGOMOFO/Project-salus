from fastapi.testclient import TestClient

from backend.main import app
from backend import mission_control_service as service


client = TestClient(app)


def test_connector_readiness_registry_state():
    state = service.get_connector_readiness_registry_state()

    assert state["status"] == "ok"
    assert state["counts"]["connectors"] >= 3
    assert state["counts"]["ready_read_only"] >= 1
    assert state["counts"]["shell_only"] >= 2
    assert state["counts"]["write_enabled"] == 0


def test_local_file_readiness_ready():
    item = service.get_connector_readiness("local_file_intelligence")

    assert item["connector_key"] == "local_file_intelligence"
    assert item["readiness_status"] == "ready_read_only"
    assert item["write_actions_blocked"] is True


def test_gmail_readiness_shell_only():
    item = service.get_connector_readiness("gmail_read_only")

    assert item["connector_key"] == "gmail_read_only"
    assert item["readiness_status"] == "shell_only"
    assert item["live_access_enabled"] is False


def test_calendar_readiness_shell_only():
    item = service.get_connector_readiness("calendar_read_only")

    assert item["connector_key"] == "calendar_read_only"
    assert item["readiness_status"] == "shell_only"
    assert item["live_access_enabled"] is False


def test_connector_readiness_registry_api():
    response = client.get("/api/mission-control/connector-readiness")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "connectors" in data


def test_connector_readiness_single_api():
    response = client.get(
        "/api/mission-control/connector-readiness/local_file_intelligence"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["connector_key"] == "local_file_intelligence"
    assert data["readiness_status"] == "ready_read_only"
