import sqlite3
from pathlib import Path

from backend import mission_control_store as store


def test_mission_control_store_connects_to_salus_db():
    assert store.db_path().name == "salus.db"


def test_mission_control_store_ensures_tables():
    with store.connect() as conn:
        store.ensure_tables(conn)

        for table in [
            "mission_control_briefs",
            "mission_control_daily_workflow",
            "mission_control_operator_queue",
        ]:
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table,),
            ).fetchone()
            assert row is not None


def test_mission_control_store_safe_rows():
    with store.connect() as conn:
        store.ensure_tables(conn)
        rows = store.safe_rows(conn, "mission_control_operator_queue", 5)
        assert isinstance(rows, list)


def test_mission_control_store_insert_dynamic():
    with store.connect() as conn:
        store.ensure_tables(conn)
        store.insert_dynamic(
            conn,
            "mission_control_operator_queue",
            {
                "title": "Store Insert Test",
                "description": "Inserted through shared store",
                "queue_type": "task",
                "status": "open",
                "priority": "high",
                "ignored_field": "ignore me",
                "created_at": "2026-01-01T00:00:00+00:00",
            },
        )
        conn.commit()

        row = conn.execute(
            "SELECT title FROM mission_control_operator_queue WHERE title=? ORDER BY id DESC LIMIT 1",
            ("Store Insert Test",),
        ).fetchone()

    assert row is not None
