import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def _db_path() -> Path:
    return Path(__file__).resolve().parents[1] / "salus.db"


def test_create_operator_queue_item():
    response = client.post(
        "/mission-control/operator-item",
        data={
            "title": "Operator Queue Test",
            "description": "Test inbox item",
            "queue_type": "task",
            "status": "open",
            "priority": "high",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/v1"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id, title, status FROM mission_control_operator_queue WHERE title = ? ORDER BY id DESC LIMIT 1",
            ("Operator Queue Test",),
        ).fetchone()

    assert row is not None
    assert row["status"] == "open"


def test_update_operator_queue_item_status():
    client.post(
        "/mission-control/operator-item",
        data={
            "title": "Operator Status Test",
            "description": "Status update test",
            "queue_type": "task",
            "priority": "high",
        },
        follow_redirects=False,
    )

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id FROM mission_control_operator_queue WHERE title = ? ORDER BY id DESC LIMIT 1",
            ("Operator Status Test",),
        ).fetchone()

    response = client.post(
        f"/mission-control/operator-item/{row['id']}/status/done",
        follow_redirects=False,
    )

    assert response.status_code == 303

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        updated = conn.execute(
            "SELECT status FROM mission_control_operator_queue WHERE id = ?",
            (row["id"],),
        ).fetchone()

    assert updated["status"] == "done"


def test_mission_control_v1_contains_operator_inbox():
    response = client.get("/mission-control/v1")
    assert response.status_code == 200
    assert "Operator Inbox" in response.text
    assert "Command Queue" in response.text
    assert "/mission-control/operator-item" in response.text
