from typing import Any

from backend.database import get_connection, init_db


def _row_to_dict(row) -> dict[str, Any]:
    return dict(row)


def create_sitrep(payload: dict[str, Any]) -> dict[str, Any]:
    init_db()

    top_priority = str(payload.get("top_priority", "")).strip()
    blocker = str(payload.get("blocker", "")).strip()
    action_1 = str(payload.get("action_1", "")).strip()
    action_2 = str(payload.get("action_2", "")).strip()
    action_3 = str(payload.get("action_3", "")).strip()

    if not top_priority:
        raise ValueError("top_priority is required")

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO sitreps (top_priority, blocker, action_1, action_2, action_3)
            VALUES (?, ?, ?, ?, ?)
            """,
            (top_priority, blocker, action_1, action_2, action_3),
        )
        conn.commit()

        sitrep_id = cur.lastrowid
        cur.execute("SELECT * FROM sitreps WHERE id = ?", (sitrep_id,))
        row = cur.fetchone()

    return _row_to_dict(row)


def list_sitreps(limit: int = 10) -> list[dict[str, Any]]:
    init_db()

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM sitreps
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()

    return [_row_to_dict(row) for row in rows]


def get_sitrep(sitrep_id: int) -> dict[str, Any] | None:
    init_db()

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM sitreps WHERE id = ?", (sitrep_id,))
        row = cur.fetchone()

    if row is None:
        return None

    return _row_to_dict(row)
