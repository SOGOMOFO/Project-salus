from fastapi.testclient import TestClient

from backend.main import app
from backend import mission_control_service as service


client = TestClient(app)


def test_connector_permission_policy_defaults():
    state = service.get_connector_permission_policy_state()

    assert state["status"] == "ok"
    assert state["counts"]["profiles"] >= 3
    assert state["counts"]["read_only"] >= 1
    assert state["counts"]["write_enabled"] == 0


def test_local_file_connector_read_allowed():
    result = service.evaluate_connector_permission(
        "local_file_intelligence",
        "read",
        "low",
    )

    assert result["decision"] == "allowed"


def test_local_file_connector_write_blocked():
    result = service.evaluate_connector_permission(
        "local_file_intelligence",
        "delete",
        "high",
    )

    assert result["decision"] == "blocked"
    assert "read-only" in result["reason"]


def test_planned_gmail_connector_blocked():
    result = service.evaluate_connector_permission(
        "gmail_read_only",
        "read",
        "medium",
    )

    assert result["decision"] == "blocked"
    assert "planned" in result["reason"]


def test_connector_permission_state_api():
    response = client.get("/api/mission-control/connector-permissions")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "profiles" in data


def test_connector_permission_profile_api():
    response = client.get(
        "/api/mission-control/connector-permissions/local_file_intelligence"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["connector_key"] == "local_file_intelligence"
    assert data["write_allowed"] is False


def test_connector_permission_evaluate_api():
    response = client.post(
        "/api/mission-control/connector-permissions/evaluate",
        params={
            "connector_key": "local_file_intelligence",
            "action_type": "read",
            "risk_level": "low",
        },
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "allowed"
