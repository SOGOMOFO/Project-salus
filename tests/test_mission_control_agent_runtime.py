from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_agent_runtime_state_api():
    response = client.get("/api/mission-control/agent-runtime")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "counts" in data
    assert "latest_events" in data
    assert "recommended_action" in data


def test_run_low_risk_task_once():
    create = client.post(
        "/api/mission-control/agent/tasks",
        json={
            "source": "runtime_test",
            "task_type": "summarize",
            "title": "Runtime Low Risk Task",
            "risk_level": "low",
            "payload": {"objective": "runtime test"},
        },
    )

    task_id = create.json()["task"]["id"]

    run = client.post(f"/api/mission-control/agent-runtime/tasks/{task_id}/run")
    assert run.status_code == 200
    assert run.json()["status"] == "completed"
    assert run.json()["task_id"] == task_id

    task = client.get(f"/api/mission-control/agent/tasks/{task_id}")
    assert task.json()["task"]["status"] == "completed"


def test_high_risk_task_blocks_until_approved_for_runtime():
    create = client.post(
        "/api/mission-control/agent/tasks",
        json={
            "source": "runtime_test",
            "task_type": "write_action",
            "title": "Runtime High Risk Task",
            "risk_level": "high",
            "payload": {"objective": "approval required"},
        },
    )

    task_id = create.json()["task"]["id"]

    blocked = client.post(f"/api/mission-control/agent-runtime/tasks/{task_id}/run")
    assert blocked.status_code == 200
    assert blocked.json()["status"] == "blocked"

    approved = client.post(f"/api/mission-control/agent/tasks/{task_id}/approve")
    assert approved.status_code == 200

    run = client.post(f"/api/mission-control/agent-runtime/tasks/{task_id}/run")
    assert run.status_code == 200
    assert run.json()["status"] == "completed"


def test_critical_task_runtime_blocked_even_after_approval():
    create = client.post(
        "/api/mission-control/agent/tasks",
        json={
            "source": "runtime_test",
            "task_type": "critical_action",
            "title": "Runtime Critical Task",
            "risk_level": "critical",
            "payload": {"objective": "blocked from auto runtime"},
        },
    )

    task_id = create.json()["task"]["id"]

    client.post(f"/api/mission-control/agent/tasks/{task_id}/approve")

    run = client.post(f"/api/mission-control/agent-runtime/tasks/{task_id}/run")
    assert run.status_code == 200
    assert run.json()["status"] == "blocked"
    assert "Critical-risk" in run.json()["reason"]


def test_runtime_batch_api():
    client.post(
        "/api/mission-control/agent/tasks",
        json={
            "source": "runtime_batch_test",
            "task_type": "summarize",
            "title": "Runtime Batch Task",
            "risk_level": "low",
            "payload": {"objective": "batch test"},
        },
    )

    response = client.post(
        "/api/mission-control/agent-runtime/run-batch",
        json={"limit": 3, "actor": "pytest_runtime"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert "results" in response.json()


def test_runtime_events_api():
    response = client.get("/api/mission-control/agent-runtime/events")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["events"], list)


def test_runtime_ui_panel_present():
    response = client.get("/mission-control/v1")
    assert response.status_code == 200

    assert "Agent Runtime Worker" in response.text
    assert "/mission-control/agent-runtime/run-next" in response.text
    assert "/api/mission-control/agent-runtime" in response.text


def test_runtime_ui_run_next():
    client.post(
        "/api/mission-control/agent/tasks",
        json={
            "source": "runtime_ui_test",
            "task_type": "summarize",
            "title": "Runtime UI Task",
            "risk_level": "low",
            "payload": {"objective": "ui runtime test"},
        },
    )

    response = client.post(
        "/mission-control/agent-runtime/run-next",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/v1"
