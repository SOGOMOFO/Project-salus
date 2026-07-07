import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def _db_path() -> Path:
    return Path(__file__).resolve().parents[1] / "salus.db"


def test_generate_missions_from_queue():
    client.post(
        "/mission-control/operator-item",
        data={
            "title": "Auto Mission Generation Test",
            "description": "Generated from command queue",
            "queue_type": "task",
            "priority": "high",
        },
        follow_redirects=False,
    )

    response = client.post(
        "/mission-control/generate-missions-from-queue",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/v1"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        mission = conn.execute(
            "SELECT title, status, priority, next_action FROM missions WHERE title = ? ORDER BY id DESC LIMIT 1",
            ("Auto Mission Generation Test",),
        ).fetchone()
        queue_item = conn.execute(
            "SELECT status FROM mission_control_operator_queue WHERE title = ? ORDER BY id DESC LIMIT 1",
            ("Auto Mission Generation Test",),
        ).fetchone()

    assert mission is not None
    assert mission["status"] == "active"
    assert mission["priority"] == "high"
    assert mission["next_action"] == "Generated from command queue"
    assert queue_item["status"] == "done"


def test_cleanup_done_queue_items():
    client.post(
        "/mission-control/operator-item",
        data={
            "title": "Cleanup Queue Test",
            "description": "Should be deleted",
            "queue_type": "task",
            "priority": "medium",
        },
        follow_redirects=False,
    )

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id FROM mission_control_operator_queue WHERE title = ? ORDER BY id DESC LIMIT 1",
            ("Cleanup Queue Test",),
        ).fetchone()

    client.post(
        f"/mission-control/operator-item/{row['id']}/status/done",
        follow_redirects=False,
    )

    response = client.post(
        "/mission-control/operator-queue/cleanup",
        follow_redirects=False,
    )

    assert response.status_code == 303

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        deleted = conn.execute(
            "SELECT id FROM mission_control_operator_queue WHERE id = ?",
            (row["id"],),
        ).fetchone()

    assert deleted is None


def test_mission_control_v1_contains_queue_generation_buttons():
    response = client.get("/mission-control/v1")
    assert response.status_code == 200
    assert "Generate Missions from Queue" in response.text
    assert "Cleanup Done Items" in response.text
