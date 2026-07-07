from fastapi.testclient import TestClient

from backend.main import app
from backend import mission_control_service as service


client = TestClient(app)


REQUIRED_CONTROLS = [
    "read_only_scope",
    "approval_gate",
    "audit_log",
    "permission_profile_check",
    "no_write_actions",
]


def test_activation_gate_blocks_unknown_connector():
    result = service.evaluate_connector_activation_gate(
        "unknown_connector",
        REQUIRED_CONTROLS,
    )

    assert result["decision"] == "blocked"


def test_activation_gate_pending_controls_when_missing():
    result = service.evaluate_connector_activation_gate(
        "local_file_intelligence",
        ["read_only_scope"],
    )

    assert result["decision"] == "pending_controls"
    assert "audit_log" in result["missing_controls"]


def test_activation_gate_local_file_ready_with_controls():
    result = service.evaluate_connector_activation_gate(
        "local_file_intelligence",
        REQUIRED_CONTROLS,
    )

    assert result["decision"] == "ready_for_read_only_activation"
    assert result["missing_controls"] == []


def test_activation_gate_gmail_pending_approval_with_controls():
    result = service.evaluate_connector_activation_gate(
        "gmail_read_only",
        REQUIRED_CONTROLS,
    )

    assert result["decision"] == "pending_approval"
    assert "not enabled" in result["reason"]


def test_activation_request_created():
    result = service.create_connector_activation_request(
        "gmail_read_only",
        REQUIRED_CONTROLS,
    )

    assert result["status"] == "ok"
    assert result["connector_key"] == "gmail_read_only"
    assert result["requires_commander_approval"] is True


def test_activation_gate_state_api():
    response = client.get("/api/mission-control/connector-activation-gate")

    assert response.status_code == 200
    data = response.json()
    assert data["counts"]["evaluated"] >= 3
    assert "required_controls" in data


def test_activation_gate_evaluate_api():
    response = client.post(
        "/api/mission-control/connector-activation-gate/evaluate",
        params={
            "connector_key": "local_file_intelligence",
            "requested_controls": REQUIRED_CONTROLS,
        },
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "ready_for_read_only_activation"


def test_activation_gate_request_api():
    response = client.post(
        "/api/mission-control/connector-activation-gate/request",
        params={
            "connector_key": "gmail_read_only",
            "requested_controls": REQUIRED_CONTROLS,
        },
    )

    assert response.status_code == 200
    assert response.json()["requires_commander_approval"] is True
