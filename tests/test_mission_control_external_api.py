import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def _db_path() -> Path:
    return Path(__file__).resolve().parents[1] / "salus.db"


def test_api_mission_control_state():
    response = client.get("/api/mission-control/state")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "readiness" in data
    assert "latest" in data
    assert "missions" in data
    assert "operator_queue" in data


def test_api_mission_control_readiness():
    response = client.get("/api/mission-control/readiness")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["posture"] in {"idle", "operational", "attention_required"}
    assert "recommended_action" in data


def test_api_create_operator_queue_item():
    response = client.post(
        "/api/mission-control/operator-queue",
        json={
            "title": "External API Queue Test",
            "description": "Created through external API",
            "queue_type": "agent_task",
            "priority": "high",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "created"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT title, description, queue_type, priority FROM mission_control_operator_queue WHERE title=? ORDER BY id DESC LIMIT 1",
            ("External API Queue Test",),
        ).fetchone()

    assert row is not None
    assert row["description"] == "Created through external API"
    assert row["queue_type"] == "agent_task"
    assert row["priority"] == "high"


def test_api_operator_queue_lists_items():
    response = client.get("/api/mission-control/operator-queue")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["operator_queue"], list)


def test_api_update_operator_queue_status():
    client.post(
        "/api/mission-control/operator-queue",
        json={
            "title": "External API Status Test",
            "description": "Update status",
            "priority": "medium",
        },
    )

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id FROM mission_control_operator_queue WHERE title=? ORDER BY id DESC LIMIT 1",
            ("External API Status Test",),
        ).fetchone()

    response = client.post(f"/api/mission-control/operator-queue/{row['id']}/status/blocked")
    assert response.status_code == 200
    assert response.json()["status"] == "updated"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        updated = conn.execute(
            "SELECT status FROM mission_control_operator_queue WHERE id=?",
            (row["id"],),
        ).fetchone()

    assert updated["status"] == "blocked"


def test_api_convert_queue_item_to_mission():
    client.post(
        "/api/mission-control/operator-queue",
        json={
            "title": "External API Convert Test",
            "description": "Convert this item",
            "priority": "high",
        },
    )

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id FROM mission_control_operator_queue WHERE title=? ORDER BY id DESC LIMIT 1",
            ("External API Convert Test",),
        ).fetchone()

    response = client.post(f"/api/mission-control/operator-queue/{row['id']}/convert-to-mission")
    assert response.status_code == 200
    assert response.json()["status"] == "converted"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        mission = conn.execute(
            "SELECT title, status, priority, next_action FROM missions WHERE title=? ORDER BY id DESC LIMIT 1",
            ("External API Convert Test",),
        ).fetchone()

    assert mission is not None
    assert mission["status"] == "active"
    assert mission["priority"] == "high"
    assert mission["next_action"] == "Convert this item"


def test_api_generate_missions_from_queue():
    client.post(
        "/api/mission-control/operator-queue",
        json={
            "title": "External API Generate Test",
            "description": "Generate from API queue",
            "priority": "high",
        },
    )

    response = client.post("/api/mission-control/operator-queue/generate-missions")
    assert response.status_code == 200
    assert response.json()["status"] == "generated"
    assert response.json()["missions_created"] >= 1

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        mission = conn.execute(
            "SELECT title, next_action FROM missions WHERE title=? ORDER BY id DESC LIMIT 1",
            ("External API Generate Test",),
        ).fetchone()

    assert mission is not None
    assert mission["next_action"] == "Generate from API queue"


def test_api_cleanup_operator_queue():
    client.post(
        "/api/mission-control/operator-queue",
        json={
            "title": "External API Cleanup Test",
            "description": "Cleanup this done item",
            "priority": "low",
        },
    )

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id FROM mission_control_operator_queue WHERE title=? ORDER BY id DESC LIMIT 1",
            ("External API Cleanup Test",),
        ).fetchone()

    client.post(f"/api/mission-control/operator-queue/{row['id']}/status/done")

    response = client.post("/api/mission-control/operator-queue/cleanup")
    assert response.status_code == 200
    assert response.json()["status"] == "cleaned"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        deleted = conn.execute(
            "SELECT id FROM mission_control_operator_queue WHERE id=?",
            (row["id"],),
        ).fetchone()

    assert deleted is None


def test_api_create_mission():
    response = client.post(
        "/api/mission-control/mission",
        json={
            "title": "External API Mission Test",
            "description": "Created through external API",
            "priority": "critical",
            "next_action": "Execute API mission",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "created"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        mission = conn.execute(
            "SELECT title, priority, next_action FROM missions WHERE title=? ORDER BY id DESC LIMIT 1",
            ("External API Mission Test",),
        ).fetchone()

    assert mission is not None
    assert mission["priority"] == "critical"
    assert mission["next_action"] == "Execute API mission"


def test_api_create_sitrep():
    response = client.post(
        "/api/mission-control/sitrep",
        json={
            "summary": "External API SITREP Test",
            "status": "green",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "created"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        sitrep = conn.execute(
            "SELECT * FROM sitreps ORDER BY id DESC LIMIT 1",
        ).fetchone()

    assert sitrep is not None
    if "status" in sitrep.keys():
        assert sitrep["status"] == "green"


def test_api_create_aar():
    response = client.post(
        "/api/mission-control/aar",
        json={
            "mission": "External API AAR Mission",
            "lesson": "External API AAR Test",
            "summary": "AAR summary",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "created"

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        columns = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(aars)").fetchall()
        }
        lesson_column = "lesson" if "lesson" in columns else "lesson_learned"
        aar = conn.execute(
            f"SELECT * FROM aars WHERE {lesson_column}=? ORDER BY id DESC LIMIT 1",
            ("External API AAR Test",),
        ).fetchone()

    assert aar is not None
    if "mission" in aar.keys():
        assert aar["mission"] == "External API AAR Mission"


def test_api_generate_commander_brief():
    response = client.post("/api/mission-control/commander-brief")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "created"
    assert "PROJECT SALUS DAILY COMMANDER BRIEF" in data["brief"]
    assert "Next Recommended Action" in data["brief"]


def test_api_latest_commander_brief():
    client.post("/api/mission-control/commander-brief")

    response = client.get("/api/mission-control/commander-brief/latest")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["latest"] is not None
    assert "brief" in data["latest"]
