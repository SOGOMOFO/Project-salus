import sqlite3
from pathlib import Path

from backend import mission_control_service as service


def _db_path() -> Path:
    return Path(__file__).resolve().parents[1] / "salus.db"


def test_service_builds_commander_brief_with_expected_action_line():
    brief = service.build_commander_brief(
        missions=[{"title": "Service Mission", "status": "active", "next_action": "Move"}],
        sitreps=[{"summary": "Green"}],
        aars=[{"lesson": "Improve handoff"}],
    )

    assert "PROJECT SALUS DAILY COMMANDER BRIEF" in brief
    assert "Next Recommended Action" in brief
    assert "Service Mission" in brief


def test_service_create_operator_item():
    service.create_operator_item(
        title="Service Queue Test",
        description="Created by service",
        queue_type="task",
        priority="high",
    )

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT title, status, priority FROM mission_control_operator_queue WHERE title=? ORDER BY id DESC LIMIT 1",
            ("Service Queue Test",),
        ).fetchone()

    assert row is not None
    assert row["status"] == "open"
    assert row["priority"] == "high"


def test_service_update_operator_status():
    service.create_operator_item("Service Status Test", "Update this")

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id FROM mission_control_operator_queue WHERE title=? ORDER BY id DESC LIMIT 1",
            ("Service Status Test",),
        ).fetchone()

    assert service.update_operator_item_status(row["id"], "done") is True

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        updated = conn.execute(
            "SELECT status FROM mission_control_operator_queue WHERE id=?",
            (row["id"],),
        ).fetchone()

    assert updated["status"] == "done"


def test_service_generate_missions_from_queue():
    service.create_operator_item(
        title="Service Generate Mission Test",
        description="Generate this mission",
        priority="high",
    )

    created = service.generate_missions_from_queue()
    assert created >= 1

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        mission = conn.execute(
            "SELECT title, status, next_action FROM missions WHERE title=? ORDER BY id DESC LIMIT 1",
            ("Service Generate Mission Test",),
        ).fetchone()

    assert mission is not None
    assert mission["status"] == "active"
    assert mission["next_action"] == "Generate this mission"


def test_service_cleanup_done_items():
    service.create_operator_item("Service Cleanup Test", "Delete when done")

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT id FROM mission_control_operator_queue WHERE title=? ORDER BY id DESC LIMIT 1",
            ("Service Cleanup Test",),
        ).fetchone()

    service.update_operator_item_status(row["id"], "done")
    deleted = service.cleanup_done_operator_items()

    assert deleted >= 1

    with sqlite3.connect(_db_path()) as conn:
        conn.row_factory = sqlite3.Row
        gone = conn.execute(
            "SELECT id FROM mission_control_operator_queue WHERE id=?",
            (row["id"],),
        ).fetchone()

    assert gone is None
