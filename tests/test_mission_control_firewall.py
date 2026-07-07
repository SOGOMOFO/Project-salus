from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_firewall_state_api():
    response = client.get("/api/mission-control/firewall")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "posture" in data
    assert "counts" in data
    assert "recommended_action" in data


def test_classify_external_actions():
    low = client.post(
        "/api/mission-control/firewall/classify",
        json={
            "connector_key": "files",
            "action_type": "read_local",
            "payload": {},
        },
    )
    assert low.status_code == 200
    assert low.json()["risk_level"] == "low"
    assert low.json()["requires_approval"] is False

    high = client.post(
        "/api/mission-control/firewall/classify",
        json={
            "connector_key": "gmail",
            "action_type": "send_email",
            "payload": {},
        },
    )
    assert high.status_code == 200
    assert high.json()["risk_level"] == "high"
    assert high.json()["requires_approval"] is True

    critical = client.post(
        "/api/mission-control/firewall/classify",
        json={
            "connector_key": "finance",
            "action_type": "send_money",
            "payload": {},
        },
    )
    assert critical.status_code == 200
    assert critical.json()["risk_level"] == "critical"
    assert critical.json()["blocked_from_auto_execute"] is True


def test_create_approve_execute_low_risk_external_action():
    create = client.post(
        "/api/mission-control/firewall/actions",
        json={
            "connector_key": "files",
            "action_type": "read_local",
            "title": "Low Risk External Action",
            "requested_by": "pytest",
            "payload": {"objective": "read local state"},
        },
    )

    assert create.status_code == 200
    action = create.json()["action"]
    assert action["status"] == "approved"
    action_id = action["id"]

    executed = client.post(f"/api/mission-control/firewall/actions/{action_id}/execute-placeholder")
    assert executed.status_code == 200
    assert executed.json()["status"] == "executed_placeholder"


def test_high_risk_external_action_requires_approval():
    create = client.post(
        "/api/mission-control/firewall/actions",
        json={
            "connector_key": "gmail",
            "action_type": "send_email",
            "title": "High Risk Email Send",
            "requested_by": "pytest",
            "payload": {"to": "test@example.com"},
        },
    )

    action = create.json()["action"]
    assert action["status"] == "pending_approval"
    action_id = action["id"]

    blocked = client.post(f"/api/mission-control/firewall/actions/{action_id}/execute-placeholder")
    assert blocked.status_code == 200
    assert blocked.json()["status"] == "blocked"

    approved = client.post(f"/api/mission-control/firewall/actions/{action_id}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    executed = client.post(f"/api/mission-control/firewall/actions/{action_id}/execute-placeholder")
    assert executed.status_code == 200
    assert executed.json()["status"] == "executed_placeholder"


def test_critical_external_action_manual_only():
    create = client.post(
        "/api/mission-control/firewall/actions",
        json={
            "connector_key": "finance",
            "action_type": "send_money",
            "title": "Critical Money Movement",
            "requested_by": "pytest",
            "payload": {"amount": 1000},
        },
    )

    action_id = create.json()["action"]["id"]

    approved = client.post(f"/api/mission-control/firewall/actions/{action_id}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved_manual_only"

    executed = client.post(f"/api/mission-control/firewall/actions/{action_id}/execute-placeholder")
    assert executed.status_code == 200
    assert executed.json()["status"] == "blocked"


def test_reject_external_action():
    create = client.post(
        "/api/mission-control/firewall/actions",
        json={
            "connector_key": "gmail",
            "action_type": "draft_email",
            "title": "Reject Draft Action",
            "requested_by": "pytest",
            "payload": {"body": "draft"},
        },
    )

    action_id = create.json()["action"]["id"]

    rejected = client.post(
        f"/api/mission-control/firewall/actions/{action_id}/reject",
        json={"reason": "pytest rejection"},
    )

    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"


def test_firewall_events_api():
    response = client.get("/api/mission-control/firewall/events")
    assert response.status_code == 200

    assert response.json()["status"] == "ok"
    assert isinstance(response.json()["events"], list)


def test_firewall_ui_panel_present():
    response = client.get("/mission-control/v1", headers={"x-salus-token": "salus-local-token"})
    assert response.status_code == 200

    assert "External Action Firewall" in response.text
    assert "/mission-control/firewall/action" in response.text
    assert "/api/mission-control/firewall" in response.text


def test_firewall_ui_request_action():
    response = client.post(
        "/mission-control/firewall/action",
        data={
            "connector_key": "gmail",
            "action_type": "draft_email",
            "title": "UI Firewall Action",
            "payload": "Draft message from UI",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/v1"
