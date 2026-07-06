import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def _db_path() -> Path:
    return Path(__file__).resolve().parents[1] / "salus.db"


def test_mission_control_status_action_redirects():
    create_response = client.post(
        "/mission-control/mission",
        data={
            "title": "Mission Status Button Test",
            "priority": "high",
            "status": "active",
            "next_action": "Click complete",
        },
        follow_redirects=False,
    )
    assert create_response.status_code == 303

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id FROM missions WHERE title = ? ORDER BY id DESC LIMIT 1",
            ("Mission Status Button Test",),
        ).fetchone()

    assert row is not None
    mission_id = row["id"]

    response = client.post(
        f"/mission-control/mission/{mission_id}/status/complete",
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/ui"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        updated = conn.execute(
            "SELECT status FROM missions WHERE id = ?",
            (mission_id,),
        ).fetchone()

    assert updated["status"] == "complete"


def test_mission_control_ui_contains_action_buttons():
    response = client.get("/mission-control/ui")
    assert response.status_code == 200
    assert "Complete" in response.text
    assert "Blocked" in response.text
    assert "Active" in response.text
