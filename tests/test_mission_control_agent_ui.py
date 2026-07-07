import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def _db_path() -> Path:
    return Path(__file__).resolve().parents[1] / "salus.db"


def test_mission_control_v1_contains_agent_execution_panel():
    response = client.get("/mission-control/v1", headers={"x-salus-token": "salus-local-token"})
    assert response.status_code == 200
    assert "Agent Execution Registry" in response.text
    assert "Agent Tasks" in response.text
    assert "Agent Audit Log" in response.text
    assert "/mission-control/agent-task" in response.text


def test_create_agent_task_from_ui():
    response = client.post(
        "/mission-control/agent-task",
        data={
            "title": "UI Agent Task Test",
            "source": "ui_test",
            "task_type": "summarize",
            "risk_level": "low",
            "payload": "Created from Mission Control UI",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/v1"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT title, source, status, risk_level FROM mission_control_agent_tasks WHERE title=? ORDER BY id DESC LIMIT 1",
            ("UI Agent Task Test",),
        ).fetchone()

    assert row is not None
    assert row["source"] == "ui_test"
    assert row["status"] == "queued"
    assert row["risk_level"] == "low"


def test_agent_task_ui_approval_flow():
    client.post(
        "/mission-control/agent-task",
        data={
            "title": "UI Approval Flow Test",
            "source": "ui_test",
            "task_type": "write_action",
            "risk_level": "high",
            "payload": "Requires commander approval",
        },
        follow_redirects=False,
    )

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        task = conn.execute(
            "SELECT id, status FROM mission_control_agent_tasks WHERE title=? ORDER BY id DESC LIMIT 1",
            ("UI Approval Flow Test",),
        ).fetchone()

    assert task is not None
    assert task["status"] == "pending_approval"

    approve = client.post(
        f"/mission-control/agent-task/{task['id']}/approve",
        follow_redirects=False,
    )

    assert approve.status_code == 303

    complete = client.post(
        f"/mission-control/agent-task/{task['id']}/complete",
        follow_redirects=False,
    )

    assert complete.status_code == 303

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        updated = conn.execute(
            "SELECT status, approved FROM mission_control_agent_tasks WHERE id=?",
            (task["id"],),
        ).fetchone()

    assert updated["status"] == "completed"
    assert updated["approved"] == 1


def test_agent_task_ui_reject_flow():
    client.post(
        "/mission-control/agent-task",
        data={
            "title": "UI Reject Flow Test",
            "source": "ui_test",
            "task_type": "critical_action",
            "risk_level": "critical",
            "payload": "Reject this task",
        },
        follow_redirects=False,
    )

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        task = conn.execute(
            "SELECT id FROM mission_control_agent_tasks WHERE title=? ORDER BY id DESC LIMIT 1",
            ("UI Reject Flow Test",),
        ).fetchone()

    reject = client.post(
        f"/mission-control/agent-task/{task['id']}/reject",
        follow_redirects=False,
    )

    assert reject.status_code == 303

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        updated = conn.execute(
            "SELECT status FROM mission_control_agent_tasks WHERE id=?",
            (task["id"],),
        ).fetchone()

    assert updated["status"] == "rejected"
