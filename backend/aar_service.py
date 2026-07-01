from typing import Any

from backend.database import get_connection, init_db


def _row_to_dict(row) -> dict[str, Any]:
    return dict(row)


def create_aar(payload: dict[str, Any]) -> dict[str, Any]:
    init_db()

    mission = str(payload.get("mission", "")).strip()
    what_happened = str(payload.get("what_happened", "")).strip()
    what_worked = str(payload.get("what_worked", "")).strip()
    what_failed = str(payload.get("what_failed", "")).strip()
    lesson_learned = str(payload.get("lesson_learned", "")).strip()
    next_action = str(payload.get("next_action", "")).strip()

    if not mission:
        raise ValueError("mission is required")

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO aars (
                mission,
                what_happened,
                what_worked,
                what_failed,
                lesson_learned,
                next_action
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                mission,
                what_happened,
                what_worked,
                what_failed,
                lesson_learned,
                next_action,
            ),
        )
        conn.commit()

        aar_id = cur.lastrowid
        cur.execute("SELECT * FROM aars WHERE id = ?", (aar_id,))
        row = cur.fetchone()

    return _row_to_dict(row)


def list_aars(limit: int = 10) -> list[dict[str, Any]]:
    init_db()

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            SELECT * FROM aars
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        )
        rows = cur.fetchall()

    return [_row_to_dict(row) for row in rows]


def get_aar(aar_id: int) -> dict[str, Any] | None:
    init_db()

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM aars WHERE id = ?", (aar_id,))
        row = cur.fetchone()

    if row is None:
        return None

    return _row_to_dict(row)
