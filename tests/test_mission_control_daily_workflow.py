import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def _db_path() -> Path:
    return Path(__file__).resolve().parents[1] / "salus.db"


def test_generate_morning_brief_persists():
    response = client.post("/mission-control/daily-workflow/morning_brief", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/ui"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT workflow_type, title, content FROM mission_control_daily_workflow ORDER BY id DESC LIMIT 1"
        ).fetchone()

    assert row is not None
    assert row["workflow_type"] == "morning_brief"
    assert row["title"] == "Morning Brief"
    assert "PROJECT SALUS MORNING BRIEF" in row["content"]


def test_generate_evening_aar_persists():
    response = client.post("/mission-control/daily-workflow/evening_aar", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/ui"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT workflow_type, title, content FROM mission_control_daily_workflow ORDER BY id DESC LIMIT 1"
        ).fetchone()

    assert row is not None
    assert row["workflow_type"] == "evening_aar"
    assert row["title"] == "Evening AAR"
    assert "PROJECT SALUS EVENING AAR" in row["content"]


def test_mission_control_ui_contains_daily_workflow_engine():
    response = client.get("/mission-control/ui", headers={"x-salus-token": "salus-local-token"})
    assert response.status_code == 200
    assert "Daily Workflow Engine" in response.text
    assert "Generate Morning Brief" in response.text
    assert "Generate Evening AAR" in response.text
