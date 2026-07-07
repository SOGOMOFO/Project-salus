from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_agent_permission_gates_seeded():
    response = client.get("/api/mission-control/agent/permission-gates")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    names = {gate["gate_name"] for gate in data["permission_gates"]}

    assert "low_risk_agent_task" in names
    assert "high_risk_agent_task" in names


def test_create_low_risk_agent_task_auto_queued():
    response = client.post(
        "/api/mission-control/agent/tasks",
        json={
            "source": "test_agent",
            "task_type": "summarize",
            "title": "Low Risk Agent Task",
            "risk_level": "low",
            "payload": {"objective": "summarize dashboard"},
        },
    )

    assert response.status_code == 200

    task = response.json()["task"]
    assert response.json()["status"] == "created"
    assert task["status"] == "queued"
    assert task["requires_approval"] == 0
    assert task["approved"] == 1


def test_create_high_risk_agent_task_requires_approval():
    response = client.post(
        "/api/mission-control/agent/tasks",
        json={
            "source": "test_agent",
            "task_type": "write_action",
            "title": "High Risk Agent Task",
            "risk_level": "high",
            "payload": {"objective": "change system state"},
        },
    )

    assert response.status_code == 200

    task = response.json()["task"]
    assert task["status"] == "pending_approval"
    assert task["requires_approval"] == 1
    assert task["approved"] == 0


def test_high_risk_task_blocks_until_approved_then_completes():
    create = client.post(
        "/api/mission-control/agent/tasks",
        json={
            "source": "test_agent",
            "task_type": "write_action",
            "title": "Approval Flow Agent Task",
            "risk_level": "high",
            "payload": {"objective": "requires approval"},
        },
    )

    task_id = create.json()["task"]["id"]

    blocked = client.post(
        f"/api/mission-control/agent/tasks/{task_id}/complete",
        json={"result": {"message": "attempt before approval"}},
    )
    assert blocked.status_code == 200
    assert blocked.json()["status"] == "blocked"
    assert blocked.json()["reason"] == "approval_required"

    approved = client.post(f"/api/mission-control/agent/tasks/{task_id}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    completed = client.post(
        f"/api/mission-control/agent/tasks/{task_id}/complete",
        json={"result": {"message": "completed after approval"}},
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"

    get_task = client.get(f"/api/mission-control/agent/tasks/{task_id}")
    assert get_task.status_code == 200
    assert get_task.json()["task"]["status"] == "completed"


def test_reject_agent_task():
    create = client.post(
        "/api/mission-control/agent/tasks",
        json={
            "source": "test_agent",
            "task_type": "critical_action",
            "title": "Rejected Agent Task",
            "risk_level": "critical",
            "payload": {"objective": "do not run"},
        },
    )

    task_id = create.json()["task"]["id"]

    rejected = client.post(
        f"/api/mission-control/agent/tasks/{task_id}/reject",
        json={"reason": "Test rejection"},
    )

    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"

    get_task = client.get(f"/api/mission-control/agent/tasks/{task_id}")
    assert get_task.json()["task"]["status"] == "rejected"


def test_agent_audit_log_records_events():
    client.post(
        "/api/mission-control/agent/tasks",
        json={
            "source": "audit_test_agent",
            "task_type": "summarize",
            "title": "Audit Log Agent Task",
            "risk_level": "low",
            "payload": {"objective": "create audit event"},
        },
    )

    response = client.get("/api/mission-control/agent/audit-log")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["audit_log"], list)
    assert any(event["action"] == "agent_task_created" for event in data["audit_log"])


def test_agent_execution_state():
    response = client.get("/api/mission-control/agent/state")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "counts" in data
    assert "tasks" in data
    assert "audit_log" in data
    assert "permission_gates" in data
