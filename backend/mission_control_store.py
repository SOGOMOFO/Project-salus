from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


def db_path() -> Path:
    return Path(__file__).resolve().parent.parent / "salus.db"


def connect() -> sqlite3.Connection:
    conn = sqlite3.connect(db_path(), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=30000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return row is not None


def ensure_tables(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS mission_control_briefs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            brief TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS mission_control_daily_workflow (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workflow_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS mission_control_operator_queue (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            queue_type TEXT NOT NULL,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    conn.commit()


def safe_rows(conn: sqlite3.Connection, table: str, limit: int = 10) -> list[dict[str, Any]]:
    if not table_exists(conn, table):
        return []

    try:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    except sqlite3.OperationalError:
        rows = conn.execute(f"SELECT * FROM {table} LIMIT ?", (limit,)).fetchall()

    return [dict(row) for row in rows]


def insert_dynamic(conn: sqlite3.Connection, table: str, values: dict[str, Any]) -> None:
    if not table_exists(conn, table):
        return

    existing_columns = {
        row["name"]
        for row in conn.execute(f"PRAGMA table_info({table})").fetchall()
    }

    payload = {
        key: value
        for key, value in values.items()
        if key in existing_columns
    }

    if not payload:
        return

    columns = ", ".join(payload.keys())
    placeholders = ", ".join(["?"] * len(payload))
    conn.execute(
        f"INSERT INTO {table} ({columns}) VALUES ({placeholders})",
        tuple(payload.values()),
    )
