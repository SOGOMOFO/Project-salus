from fastapi.testclient import TestClient

from backend.main import app
from backend import mission_control_service as service


client = TestClient(app)


def test_gmail_read_only_shell_state():
    state = service.get_gmail_read_only_connector_state()

    assert state["status"] == "ok"
    assert state["connector_key"] == "gmail_read_only"
    assert state["mode"] == "shell"
    assert state["live_access_enabled"] is False
    assert state["read_only"] is True
    assert state["write_actions_blocked"] is True


def test_gmail_read_only_blocks_send():
    result = service.evaluate_gmail_read_only_request(
        "send",
        "high",
    )

    assert result["decision"] == "blocked"
    assert "read-only" in result["reason"]


def test_gmail_read_only_read_is_blocked_until_activation():
    result = service.evaluate_gmail_read_only_request(
        "read",
        "medium",
    )

    assert result["decision"] == "blocked"
    assert "planned" in result["reason"]


def test_gmail_read_only_activation_plan():
    plan = service.get_gmail_read_only_activation_plan()

    assert plan["status"] == "planned"
    assert "read_only_scope" in plan["required_controls"]
    assert "no_write_actions" in plan["required_controls"]


def test_gmail_read_only_state_api():
    response = client.get("/api/mission-control/gmail-read-only")

    assert response.status_code == 200
    data = response.json()
    assert data["connector_key"] == "gmail_read_only"
    assert data["live_access_enabled"] is False


def test_gmail_read_only_capabilities_api():
    response = client.get("/api/mission-control/gmail-read-only/capabilities")

    assert response.status_code == 200
    data = response.json()
    assert data["connector_key"] == "gmail_read_only"
    assert len(data["capabilities"]) >= 3


def test_gmail_read_only_evaluate_api_blocks_send():
    response = client.post(
        "/api/mission-control/gmail-read-only/evaluate",
        params={
            "action_type": "send",
            "risk_level": "high",
        },
    )

    assert response.status_code == 200
    assert response.json()["decision"] == "blocked"


def test_gmail_read_only_activation_plan_api():
    response = client.get("/api/mission-control/gmail-read-only/activation-plan")

    assert response.status_code == 200
    assert response.json()["status"] == "planned"
