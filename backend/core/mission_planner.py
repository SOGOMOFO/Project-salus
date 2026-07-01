from __future__ import annotations

from typing import Any, Optional

from backend.database import get_connection
from backend.memory.memory_engine import add_memory, initialize_memory_store

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


class MissionPlanner:
    def initialize(self) -> None:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS core_missions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
            """
        )
        conn.commit()
        conn.close()

    def create_mission(
        self,
        *,
        title: str,
        description: str = "",
        priority: str = "medium",
    ) -> dict[str, Any]:
        self.initialize()
        normalized_title = str(title or "").strip()
        if not normalized_title:
            raise ValueError("title is required")

        normalized_priority = _normalize_priority(priority)
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO core_missions (title, description, priority, status)
            VALUES (?, ?, ?, 'open')
            """,
            (normalized_title, str(description or "").strip(), normalized_priority),
        )
        conn.commit()
        mission_id = cur.lastrowid
        row = cur.execute(
            """
            SELECT id, title, description, priority, status, created_at, completed_at
            FROM core_missions
            WHERE id = ?
            """,
            (mission_id,),
        ).fetchone()
        conn.close()

        mission = _mission_row_to_dict(row)
        try:
            initialize_memory_store()
            add_memory(
                memory_type="mission",
                title=mission["title"],
                content=mission["description"] or mission["title"],
                tags=["mission-planner", mission["priority"]],
                source="mission-planner",
            )
        except Exception:
            pass
        return mission

    def list_missions(self, status: Optional[str] = None) -> list[dict[str, Any]]:
        self.initialize()
        conn = get_connection()
        cur = conn.cursor()
        order_clause = """
            ORDER BY
                CASE priority
                    WHEN 'high' THEN 0
                    WHEN 'medium' THEN 1
                    WHEN 'low' THEN 2
                    ELSE 3
                END,
                datetime(created_at) DESC,
                id DESC
        """
        if status:
            rows = cur.execute(
                """
                SELECT id, title, description, priority, status, created_at, completed_at
                FROM core_missions
                WHERE status = ?
                """ + order_clause,
                (str(status).strip().lower(),),
            ).fetchall()
        else:
            rows = cur.execute(
                """
                SELECT id, title, description, priority, status, created_at, completed_at
                FROM core_missions
                """ + order_clause
            ).fetchall()
        conn.close()
        return [_mission_row_to_dict(row) for row in rows]

    def complete_mission(self, mission_id: int) -> dict[str, Any] | None:
        self.initialize()
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE core_missions
            SET status = 'completed', completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (int(mission_id),),
        )
        conn.commit()
        row = cur.execute(
            """
            SELECT id, title, description, priority, status, created_at, completed_at
            FROM core_missions
            WHERE id = ?
            """,
            (int(mission_id),),
        ).fetchone()
        conn.close()
        if not row:
            return None
        return _mission_row_to_dict(row)

    def update_mission(
        self,
        mission_id: int,
        *,
        title: str | None = None,
        description: str | None = None,
        priority: str | None = None,
        status: str | None = None,
    ) -> dict[str, Any] | None:
        self.initialize()
        conn = get_connection()
        cur = conn.cursor()

        row = cur.execute(
            """
            SELECT id, title, description, priority, status, created_at, completed_at
            FROM core_missions
            WHERE id = ?
            """,
            (int(mission_id),),
        ).fetchone()

        if not row:
            conn.close()
            return None

        current = _mission_row_to_dict(row)

        new_title = str(title).strip() if title is not None else current["title"]
        new_description = (
            str(description).strip() if description is not None else current["description"]
        )
        new_priority = _normalize_priority(priority) if priority is not None else current["priority"]
        new_status = _normalize_status(status) if status is not None else current["status"]

        completed_at_sql = "completed_at"
        if new_status == "completed" and not current["completed_at"]:
            completed_at_sql = "CURRENT_TIMESTAMP"
        elif new_status != "completed":
            completed_at_sql = "NULL"

        cur.execute(
            f"""
            UPDATE core_missions
            SET title = ?,
                description = ?,
                priority = ?,
                status = ?,
                completed_at = {completed_at_sql}
            WHERE id = ?
            """,
            (new_title, new_description, new_priority, new_status, int(mission_id)),
        )
        conn.commit()

        updated = cur.execute(
            """
            SELECT id, title, description, priority, status, created_at, completed_at
            FROM core_missions
            WHERE id = ?
            """,
            (int(mission_id),),
        ).fetchone()
        conn.close()

        return _mission_row_to_dict(updated)



def _normalize_priority(priority: str | None) -> str:
    normalized = str(priority or "medium").strip().lower()
    if normalized not in PRIORITY_ORDER:
        return "medium"
    return normalized


def _normalize_status(status: str | None) -> str:
    normalized = str(status or "open").strip().lower()
    allowed = {"open", "active", "blocked", "paused", "completed"}
    if normalized not in allowed:
        return "open"
    return normalized


def _mission_row_to_dict(row: Any) -> dict[str, Any]:
    return {
        "id": row[0],
        "title": row[1],
        "description": row[2],
        "priority": _normalize_priority(row[3]),
        "status": row[4],
        "created_at": row[5],
        "completed_at": row[6],
    }
