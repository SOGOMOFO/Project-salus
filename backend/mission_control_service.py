from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend import mission_control_store as store


def value(row: dict[str, Any] | None, *keys: str, default: str = "") -> str:
    if not row:
        return default
    for key in keys:
        item = row.get(key)
        if item not in (None, ""):
            return str(item)
    return default


def build_commander_brief(
    missions: list[dict[str, Any]],
    sitreps: list[dict[str, Any]],
    aars: list[dict[str, Any]],
) -> str:
    active = [m for m in missions if str(m.get("status", "")).lower() == "active"]
    blocked = [m for m in missions if str(m.get("status", "")).lower() == "blocked"]

    latest_mission = missions[0] if missions else {}
    latest_sitrep = sitreps[0] if sitreps else {}
    latest_aar = aars[0] if aars else {}

    lines = [
        "PROJECT SALUS DAILY COMMANDER BRIEF",
        "",
        f"Active missions: {len(active)}",
        f"Blocked missions: {len(blocked)}",
        "",
        f"Primary mission: {value(latest_mission, 'title', 'name', default='No active mission')}",
        f"Mission status: {value(latest_mission, 'status', default='unknown')}",
        f"Next action: {value(latest_mission, 'next_action', 'description', default='Define next action.')}",
        "",
        f"Latest SITREP: {value(latest_sitrep, 'summary', 'content', 'status', default='No SITREP recorded.')}",
        f"Latest AAR lesson: {value(latest_aar, 'lesson_learned', 'lesson', 'summary', default='No AAR lesson recorded.')}",
        "",
        "Next Recommended Action: Execute the highest-priority active mission and clear blockers.",
        "",
        "Commander guidance:",
        "1. Clear blocked missions.",
        "2. Execute the highest-priority active mission.",
        "3. Capture SITREP and AAR before shutdown.",
    ]

    return "\n".join(str(line) if line is not None else "" for line in lines)


def create_commander_brief() -> str:
    with store.connect() as conn:
        store.ensure_tables(conn)
        missions = store.safe_rows(conn, "missions", 50)
        sitreps = store.safe_rows(conn, "sitreps", 10)
        aars = store.safe_rows(conn, "aars", 10)

        brief = build_commander_brief(missions, sitreps, aars)

        store.insert_dynamic(
            conn,
            "mission_control_briefs",
            {
                "title": "Daily Commander Brief",
                "brief": brief,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        conn.commit()

    return brief


def create_operator_item(
    title: str,
    description: str = "",
    queue_type: str = "task",
    status: str = "open",
    priority: str = "medium",
) -> None:
    with store.connect() as conn:
        store.ensure_tables(conn)
        store.insert_dynamic(
            conn,
            "mission_control_operator_queue",
            {
                "title": title or "Untitled Operator Item",
                "description": description or "",
                "queue_type": queue_type or "task",
                "status": status or "open",
                "priority": priority or "medium",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        conn.commit()


def update_operator_item_status(item_id: int, status: str) -> bool:
    allowed = {"open", "in_progress", "done", "blocked"}
    if status not in allowed:
        return False

    with store.connect() as conn:
        store.ensure_tables(conn)
        conn.execute(
            "UPDATE mission_control_operator_queue SET status = ? WHERE id = ?",
            (status, item_id),
        )
        conn.commit()

    return True


def convert_operator_item_to_mission(item_id: int) -> bool:
    with store.connect() as conn:
        store.ensure_tables(conn)

        item = conn.execute(
            "SELECT * FROM mission_control_operator_queue WHERE id = ?",
            (item_id,),
        ).fetchone()

        if item is None:
            return False

        row = dict(item)

        store.insert_dynamic(
            conn,
            "missions",
            {
                "title": row.get("title") or "Converted Mission",
                "status": "active",
                "priority": row.get("priority") or "medium",
                "next_action": row.get("description") or "Define next action.",
            },
        )

        conn.execute(
            "UPDATE mission_control_operator_queue SET status = ? WHERE id = ?",
            ("done", item_id),
        )
        conn.commit()

    return True


def generate_missions_from_queue() -> int:
    created = 0

    with store.connect() as conn:
        store.ensure_tables(conn)

        rows = conn.execute(
            """
            SELECT * FROM mission_control_operator_queue
            WHERE status IN ('open', 'in_progress')
            ORDER BY
              CASE priority
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                WHEN 'low' THEN 4
                ELSE 5
              END,
              id ASC
            """
        ).fetchall()

        for item in rows:
            row = dict(item)
            store.insert_dynamic(
                conn,
                "missions",
                {
                    "title": row.get("title") or "Generated Mission",
                    "status": "active",
                    "priority": row.get("priority") or "medium",
                    "next_action": row.get("description") or "Define next action.",
                },
            )
            conn.execute(
                "UPDATE mission_control_operator_queue SET status = ? WHERE id = ?",
                ("done", row["id"]),
            )
            created += 1

        conn.commit()

    return created


def cleanup_done_operator_items() -> int:
    with store.connect() as conn:
        store.ensure_tables(conn)
        cursor = conn.execute(
            "DELETE FROM mission_control_operator_queue WHERE status = ?",
            ("done",),
        )
        conn.commit()
        return cursor.rowcount
