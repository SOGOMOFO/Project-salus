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


def get_mission_control_state() -> dict[str, Any]:
    with store.connect() as conn:
        store.ensure_tables(conn)

        missions = store.safe_rows(conn, "missions", 100)
        sitreps = store.safe_rows(conn, "sitreps", 25)
        aars = store.safe_rows(conn, "aars", 25)
        briefs = store.safe_rows(conn, "mission_control_briefs", 10)
        workflows = store.safe_rows(conn, "mission_control_daily_workflow", 10)
        queue = store.safe_rows(conn, "mission_control_operator_queue", 100)

    active_missions = [
        mission for mission in missions
        if str(mission.get("status", "")).lower() == "active"
    ]
    blocked_missions = [
        mission for mission in missions
        if str(mission.get("status", "")).lower() == "blocked"
    ]
    complete_missions = [
        mission for mission in missions
        if str(mission.get("status", "")).lower() in {"complete", "completed", "done"}
    ]
    open_queue = [
        item for item in queue
        if str(item.get("status", "")).lower() in {"open", "in_progress", "blocked"}
    ]

    return {
        "status": "ok",
        "readiness": {
            "active_missions": len(active_missions),
            "blocked_missions": len(blocked_missions),
            "complete_missions": len(complete_missions),
            "open_queue_items": len(open_queue),
            "total_missions": len(missions),
            "total_queue_items": len(queue),
        },
        "latest": {
            "mission": missions[0] if missions else None,
            "sitrep": sitreps[0] if sitreps else None,
            "aar": aars[0] if aars else None,
            "brief": briefs[0] if briefs else None,
            "workflow": workflows[0] if workflows else None,
            "queue_item": queue[0] if queue else None,
        },
        "missions": missions,
        "operator_queue": queue,
        "sitreps": sitreps,
        "aars": aars,
        "briefs": briefs,
        "workflows": workflows,
    }


def list_operator_queue(limit: int = 100) -> list[dict[str, Any]]:
    with store.connect() as conn:
        store.ensure_tables(conn)
        return store.safe_rows(conn, "mission_control_operator_queue", limit)


def get_latest_commander_brief() -> dict[str, Any] | None:
    with store.connect() as conn:
        store.ensure_tables(conn)
        rows = store.safe_rows(conn, "mission_control_briefs", 1)
        return rows[0] if rows else None


def get_readiness_snapshot() -> dict[str, Any]:
    state = get_mission_control_state()
    readiness = state["readiness"]

    if readiness["blocked_missions"] > 0:
        posture = "attention_required"
    elif readiness["active_missions"] > 0:
        posture = "operational"
    else:
        posture = "idle"

    return {
        "status": "ok",
        "posture": posture,
        "readiness": readiness,
        "recommended_action": _readiness_recommendation(readiness),
    }


def _readiness_recommendation(readiness: dict[str, Any]) -> str:
    if readiness["blocked_missions"] > 0:
        return "Clear blocked missions before adding new work."
    if readiness["open_queue_items"] > 0 and readiness["active_missions"] < 3:
        return "Convert the highest-priority queue item into an active mission."
    if readiness["active_missions"] == 0:
        return "Create or generate one active mission."
    return "Execute the highest-priority active mission and capture SITREP before shutdown."


def create_mission_from_payload(payload: dict[str, Any]) -> None:
    with store.connect() as conn:
        store.ensure_tables(conn)
        store.insert_dynamic(
            conn,
            "missions",
            {
                "title": payload.get("title") or payload.get("name") or "API Mission",
                "name": payload.get("name") or payload.get("title") or "API Mission",
                "status": payload.get("status") or "active",
                "priority": payload.get("priority") or "medium",
                "next_action": payload.get("next_action") or payload.get("description") or "Define next action.",
                "description": payload.get("description") or payload.get("next_action") or "",
            },
        )
        conn.commit()


def create_sitrep_from_payload(payload: dict[str, Any]) -> None:
    summary = payload.get("summary") or payload.get("content") or "API SITREP"

    with store.connect() as conn:
        store.ensure_tables(conn)
        store.insert_dynamic(
            conn,
            "sitreps",
            {
                "summary": summary,
                "content": summary,
                "status": payload.get("status") or "green",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        conn.commit()


def create_aar_from_payload(payload: dict[str, Any]) -> None:
    lesson = payload.get("lesson") or payload.get("lesson_learned") or payload.get("summary") or "API AAR"
    mission = payload.get("mission") or payload.get("mission_name") or payload.get("title") or "General"

    with store.connect() as conn:
        store.ensure_tables(conn)
        store.insert_dynamic(
            conn,
            "aars",
            {
                "mission": mission,
                "mission_name": mission,
                "summary": payload.get("summary") or lesson,
                "lesson": lesson,
                "lesson_learned": lesson,
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        )
        conn.commit()
