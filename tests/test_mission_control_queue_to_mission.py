import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def _db_path() -> Path:
    return Path(__file__).resolve().parents[1] / "salus.db"


def test_convert_operator_queue_item_to_mission():
    create = client.post(
        "/mission-control/operator-item",
        data={
            "title": "Convert Queue Item Test",
            "description": "Converted from operator queue",
            "queue_type": "task",
            "priority": "high",
        },
        follow_redirects=False,
    )
    assert create.status_code == 303

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        item = conn.execute(
            "SELECT id FROM mission_control_operator_queue WHERE title = ? ORDER BY id DESC LIMIT 1",
            ("Convert Queue Item Test",),
        ).fetchone()

    assert item is not None

    response = client.post(
        f"/mission-control/operator-item/{item['id']}/convert-to-mission",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/v1"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        mission = conn.execute(
            "SELECT title, status, priority, next_action FROM missions WHERE title = ? ORDER BY id DESC LIMIT 1",
            ("Convert Queue Item Test",),
        ).fetchone()
        queue_item = conn.execute(
            "SELECT status FROM mission_control_operator_queue WHERE id = ?",
            (item["id"],),
        ).fetchone()

    assert mission is not None
    assert mission["status"] == "active"
    assert mission["priority"] == "high"
    assert mission["next_action"] == "Converted from operator queue"
    assert queue_item["status"] == "done"


def test_mission_control_v1_contains_convert_to_mission_button():
    response = client.get("/mission-control/v1", headers={"x-salus-token": "salus-local-token"})
    assert response.status_code == 200
    assert "Convert to Mission" in response.text
