import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def _db_path() -> Path:
    return Path(__file__).resolve().parents[1] / "salus.db"


def test_generate_commander_brief_redirects_and_persists():
    response = client.post(
        "/mission-control/commander-brief",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/ui"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT title, brief FROM mission_control_briefs ORDER BY id DESC LIMIT 1"
        ).fetchone()

    assert row is not None
    assert row["title"] == "Daily Commander Brief"
    assert "PROJECT SALUS DAILY COMMANDER BRIEF" in row["brief"]
    assert "Next Recommended Action" in row["brief"]


def test_mission_control_ui_contains_commander_brief_button():
    response = client.get("/mission-control/ui")

    assert response.status_code == 200
    assert "Daily Commander Brief" in response.text
    assert "Generate Commander Brief" in response.text
