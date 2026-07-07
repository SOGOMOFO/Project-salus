import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def _db_path() -> Path:
    return Path(__file__).resolve().parents[1] / "salus.db"


def test_agent_risk_dashboard_api():
    response = client.get("/api/mission-control/agent/risk-dashboard")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "posture" in data
    assert "counts" in data
    assert "by_risk" in data
    assert "recommended_action" in data


def test_agent_task_filter_api():
    client.post(
        "/api/mission-control/agent/tasks",
        json={
            "source": "filter_test",
            "task_type": "summarize",
            "title": "Filter Low Risk Task",
            "risk_level": "low",
            "payload": {"objective": "filter test"},
        },
    )

    response = client.get("/api/mission-control/agent/tasks/filter?risk_level=low")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert isinstance(response.json()["tasks"], list)
    assert any(task["risk_level"] == "low" for task in response.json()["tasks"])


def test_promote_low_risk_agent_task_to_mission_api():
    create = client.post(
        "/api/mission-control/agent/tasks",
        json={
            "source": "promotion_test",
            "task_type": "summarize",
            "title": "Promote Agent Task API Test",
            "risk_level": "low",
            "payload": {"objective": "Turn this task into a mission"},
        },
    )

    task_id = create.json()["task"]["id"]

    response = client.post(f"/api/mission-control/agent/tasks/{task_id}/promote-to-mission")
    assert response.status_code == 200
    assert response.json()["status"] == "promoted"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        mission = conn.execute(
            "SELECT title, status, next_action FROM missions WHERE title=? ORDER BY id DESC LIMIT 1",
            ("Promote Agent Task API Test",),
        ).fetchone()
        task = conn.execute(
            "SELECT status FROM mission_control_agent_tasks WHERE id=?",
            (task_id,),
        ).fetchone()

    assert mission is not None
    assert mission["status"] == "active"
    assert mission["next_action"] == "Turn this task into a mission"
    assert task["status"] == "promoted_to_mission"


def test_high_risk_promotion_requires_approval():
    create = client.post(
        "/api/mission-control/agent/tasks",
        json={
            "source": "promotion_test",
            "task_type": "write_action",
            "title": "Blocked Promotion Agent Task",
            "risk_level": "high",
            "payload": {"objective": "Should require approval"},
        },
    )

    task_id = create.json()["task"]["id"]

    blocked = client.post(f"/api/mission-control/agent/tasks/{task_id}/promote-to-mission")
    assert blocked.status_code == 200
    assert blocked.json()["status"] == "blocked"

    approved = client.post(f"/api/mission-control/agent/tasks/{task_id}/approve")
    assert approved.status_code == 200

    promoted = client.post(f"/api/mission-control/agent/tasks/{task_id}/promote-to-mission")
    assert promoted.status_code == 200
    assert promoted.json()["status"] == "promoted"


def test_v1_contains_risk_dashboard_and_promotion_button():
    response = client.get("/mission-control/v1", headers={"x-salus-token": "salus-local-token"})
    assert response.status_code == 200
    assert "Agent Risk Dashboard" in response.text
    assert "Promote to Mission" in response.text
    assert "/promote-to-mission" in response.text


def test_ui_promote_agent_task_to_mission():
    create = client.post(
        "/mission-control/agent-task",
        data={
            "title": "UI Promote Agent Task Test",
            "source": "ui_promotion_test",
            "task_type": "summarize",
            "risk_level": "low",
            "payload": "Promote through UI",
        },
        follow_redirects=False,
    )
    assert create.status_code == 303

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        task = conn.execute(
            "SELECT id FROM mission_control_agent_tasks WHERE title=? ORDER BY id DESC LIMIT 1",
            ("UI Promote Agent Task Test",),
        ).fetchone()

    response = client.post(
        f"/mission-control/agent-task/{task['id']}/promote-to-mission",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/v1"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        mission = conn.execute(
            "SELECT title, status FROM missions WHERE title=? ORDER BY id DESC LIMIT 1",
            ("UI Promote Agent Task Test",),
        ).fetchone()

    assert mission is not None
    assert mission["status"] == "active"
