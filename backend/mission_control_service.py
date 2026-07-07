from __future__ import annotations
from pathlib import Path

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


def ensure_agent_execution_tables() -> None:
    with store.connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_agent_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source TEXT NOT NULL,
                task_type TEXT NOT NULL,
                title TEXT NOT NULL,
                payload TEXT NOT NULL,
                status TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                requires_approval INTEGER NOT NULL,
                approved INTEGER NOT NULL,
                result TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor TEXT NOT NULL,
                action TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id TEXT NOT NULL,
                detail TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_permission_gates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                gate_name TEXT NOT NULL UNIQUE,
                risk_level TEXT NOT NULL,
                allowed_without_approval INTEGER NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        now = datetime.now(timezone.utc).isoformat()
        gates = [
            ("low_risk_agent_task", "low", 1, "Low-risk read, summarize, organize, and draft tasks may run without approval."),
            ("medium_risk_agent_task", "medium", 0, "Medium-risk tasks require commander approval before execution."),
            ("high_risk_agent_task", "high", 0, "High-risk tasks require explicit approval and audit logging."),
            ("critical_risk_agent_task", "critical", 0, "Critical actions are blocked until explicitly approved."),
        ]

        for gate_name, risk_level, allowed, description in gates:
            conn.execute(
                """
                INSERT OR IGNORE INTO mission_control_permission_gates
                (gate_name, risk_level, allowed_without_approval, description, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (gate_name, risk_level, allowed, description, now),
            )

        conn.commit()


def audit_log(actor: str, action: str, target_type: str, target_id: str, detail: str) -> None:
    ensure_agent_execution_tables()

    with store.connect() as conn:
        conn.execute(
            """
            INSERT INTO mission_control_audit_log
            (actor, action, target_type, target_id, detail, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                actor or "system",
                action or "unknown_action",
                target_type or "unknown_target",
                str(target_id or "unknown"),
                detail or "",
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        conn.commit()


def _agent_task_requires_approval(risk_level: str, explicit_requires_approval: bool = False) -> bool:
    risk = str(risk_level or "medium").lower()
    if explicit_requires_approval:
        return True
    return risk in {"medium", "high", "critical"}


def create_agent_task_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    import json

    ensure_agent_execution_tables()

    risk_level = str(payload.get("risk_level") or "medium").lower()
    requires_approval = _agent_task_requires_approval(
        risk_level,
        bool(payload.get("requires_approval", False)),
    )

    status = "pending_approval" if requires_approval else "queued"
    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO mission_control_agent_tasks
            (source, task_type, title, payload, status, risk_level, requires_approval, approved, result, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.get("source") or "external_agent",
                payload.get("task_type") or "general",
                payload.get("title") or "Untitled Agent Task",
                json.dumps(payload.get("payload") or payload),
                status,
                risk_level,
                1 if requires_approval else 0,
                0 if requires_approval else 1,
                None,
                now,
                now,
            ),
        )
        task_id = cursor.lastrowid
        conn.commit()

    audit_log(
        actor=payload.get("source") or "external_agent",
        action="agent_task_created",
        target_type="agent_task",
        target_id=str(task_id),
        detail=f"Created agent task with risk={risk_level} status={status}",
    )

    return get_agent_task(task_id) or {"id": task_id, "status": status}


def get_agent_task(task_id: int) -> dict[str, Any] | None:
    ensure_agent_execution_tables()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        row = conn.execute(
            "SELECT * FROM mission_control_agent_tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

    return dict(row) if row else None


def list_agent_tasks(limit: int = 100) -> list[dict[str, Any]]:
    ensure_agent_execution_tables()

    with store.connect() as conn:
        rows = conn.execute(
            "SELECT * FROM mission_control_agent_tasks ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def approve_agent_task(task_id: int, actor: str = "commander") -> bool:
    ensure_agent_execution_tables()
    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        row = conn.execute(
            "SELECT id FROM mission_control_agent_tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        if row is None:
            return False

        conn.execute(
            """
            UPDATE mission_control_agent_tasks
            SET approved = 1, status = ?, updated_at = ?
            WHERE id = ?
            """,
            ("queued", now, task_id),
        )
        conn.commit()

    audit_log(
        actor=actor,
        action="agent_task_approved",
        target_type="agent_task",
        target_id=str(task_id),
        detail="Commander approved agent task for execution.",
    )

    return True


def reject_agent_task(task_id: int, actor: str = "commander", reason: str = "") -> bool:
    ensure_agent_execution_tables()
    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        row = conn.execute(
            "SELECT id FROM mission_control_agent_tasks WHERE id = ?",
            (task_id,),
        ).fetchone()

        if row is None:
            return False

        conn.execute(
            """
            UPDATE mission_control_agent_tasks
            SET approved = 0, status = ?, result = ?, updated_at = ?
            WHERE id = ?
            """,
            ("rejected", reason or "Rejected by commander.", now, task_id),
        )
        conn.commit()

    audit_log(
        actor=actor,
        action="agent_task_rejected",
        target_type="agent_task",
        target_id=str(task_id),
        detail=reason or "Commander rejected agent task.",
    )

    return True


def complete_agent_task(task_id: int, result: dict[str, Any] | None = None, actor: str = "agent_runtime") -> dict[str, Any]:
    import json

    ensure_agent_execution_tables()
    now = datetime.now(timezone.utc).isoformat()

    task = get_agent_task(task_id)
    if not task:
        return {"status": "not_found", "task_id": task_id}

    if int(task.get("requires_approval") or 0) == 1 and int(task.get("approved") or 0) != 1:
        audit_log(
            actor=actor,
            action="agent_task_execution_blocked",
            target_type="agent_task",
            target_id=str(task_id),
            detail="Execution blocked because approval is required.",
        )
        return {"status": "blocked", "reason": "approval_required", "task_id": task_id}

    with store.connect() as conn:
        conn.execute(
            """
            UPDATE mission_control_agent_tasks
            SET status = ?, result = ?, updated_at = ?
            WHERE id = ?
            """,
            ("completed", json.dumps(result or {"message": "completed"}), now, task_id),
        )
        conn.commit()

    audit_log(
        actor=actor,
        action="agent_task_completed",
        target_type="agent_task",
        target_id=str(task_id),
        detail="Agent task marked completed.",
    )

    return {"status": "completed", "task_id": task_id}


def list_audit_log(limit: int = 100) -> list[dict[str, Any]]:
    ensure_agent_execution_tables()

    with store.connect() as conn:
        rows = conn.execute(
            "SELECT * FROM mission_control_audit_log ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def list_permission_gates() -> list[dict[str, Any]]:
    ensure_agent_execution_tables()

    with store.connect() as conn:
        rows = conn.execute(
            "SELECT * FROM mission_control_permission_gates ORDER BY id ASC",
        ).fetchall()

    return [dict(row) for row in rows]


def get_agent_execution_state() -> dict[str, Any]:
    tasks = list_agent_tasks(100)
    audit = list_audit_log(50)
    gates = list_permission_gates()

    pending = [task for task in tasks if task.get("status") == "pending_approval"]
    queued = [task for task in tasks if task.get("status") == "queued"]
    completed = [task for task in tasks if task.get("status") == "completed"]
    blocked = [task for task in tasks if task.get("status") == "blocked"]

    return {
        "status": "ok",
        "counts": {
            "total_tasks": len(tasks),
            "pending_approval": len(pending),
            "queued": len(queued),
            "completed": len(completed),
            "blocked": len(blocked),
            "audit_events": len(audit),
            "permission_gates": len(gates),
        },
        "latest_task": tasks[0] if tasks else None,
        "tasks": tasks,
        "audit_log": audit,
        "permission_gates": gates,
    }


def promote_agent_task_to_mission(task_id: int, actor: str = "commander") -> dict[str, Any]:
    import json

    ensure_agent_execution_tables()
    task = get_agent_task(task_id)

    if not task:
        return {"status": "not_found", "task_id": task_id}

    if int(task.get("requires_approval") or 0) == 1 and int(task.get("approved") or 0) != 1:
        audit_log(
            actor=actor,
            action="agent_task_promotion_blocked",
            target_type="agent_task",
            target_id=str(task_id),
            detail="Promotion blocked because task requires approval.",
        )
        return {"status": "blocked", "reason": "approval_required", "task_id": task_id}

    payload_text = task.get("payload") or "{}"
    try:
        payload = json.loads(payload_text)
    except Exception:
        payload = {}

    objective = payload.get("objective") or payload.get("description") or task.get("title") or "Promoted agent task."

    with store.connect() as conn:
        store.ensure_tables(conn)
        store.insert_dynamic(
            conn,
            "missions",
            {
                "title": task.get("title") or "Promoted Agent Mission",
                "name": task.get("title") or "Promoted Agent Mission",
                "status": "active",
                "priority": _priority_from_risk(task.get("risk_level")),
                "next_action": objective,
                "description": objective,
            },
        )

        conn.execute(
            """
            UPDATE mission_control_agent_tasks
            SET status = ?, result = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                "promoted_to_mission",
                json.dumps({"mission_title": task.get("title"), "objective": objective}),
                datetime.now(timezone.utc).isoformat(),
                task_id,
            ),
        )
        conn.commit()

    audit_log(
        actor=actor,
        action="agent_task_promoted_to_mission",
        target_type="agent_task",
        target_id=str(task_id),
        detail=f"Promoted agent task '{task.get('title')}' into active mission.",
    )

    return {"status": "promoted", "task_id": task_id, "mission_title": task.get("title")}


def _priority_from_risk(risk_level: str | None) -> str:
    risk = str(risk_level or "medium").lower()
    if risk in {"critical", "high"}:
        return "high"
    if risk == "low":
        return "low"
    return "medium"


def get_agent_risk_dashboard() -> dict[str, Any]:
    ensure_agent_execution_tables()
    tasks = list_agent_tasks(250)

    by_risk = {
        "low": 0,
        "medium": 0,
        "high": 0,
        "critical": 0,
        "unknown": 0,
    }

    by_status: dict[str, int] = {}
    pending_approval = []
    blocked = []
    executable = []

    for task in tasks:
        risk = str(task.get("risk_level") or "unknown").lower()
        if risk not in by_risk:
            risk = "unknown"
        by_risk[risk] += 1

        status = str(task.get("status") or "unknown").lower()
        by_status[status] = by_status.get(status, 0) + 1

        if status == "pending_approval":
            pending_approval.append(task)
        if status == "blocked":
            blocked.append(task)
        if status == "queued" and int(task.get("approved") or 0) == 1:
            executable.append(task)

    if by_risk["critical"] > 0 or by_risk["high"] > 3:
        posture = "elevated"
    elif pending_approval:
        posture = "approval_required"
    elif executable:
        posture = "ready"
    else:
        posture = "idle"

    return {
        "status": "ok",
        "posture": posture,
        "counts": {
            "total": len(tasks),
            "pending_approval": len(pending_approval),
            "blocked": len(blocked),
            "executable": len(executable),
        },
        "by_risk": by_risk,
        "by_status": by_status,
        "pending_approval": pending_approval[:25],
        "blocked": blocked[:25],
        "executable": executable[:25],
        "recommended_action": _agent_risk_recommendation(posture, pending_approval, executable, blocked),
    }


def _agent_risk_recommendation(
    posture: str,
    pending_approval: list[dict[str, Any]],
    executable: list[dict[str, Any]],
    blocked: list[dict[str, Any]],
) -> str:
    if posture == "elevated":
        return "Review high and critical risk tasks before allowing further execution."
    if pending_approval:
        return "Approve, reject, or convert the oldest pending agent task."
    if blocked:
        return "Clear blocked agent tasks or reject stale work."
    if executable:
        return "Execute or promote the highest-value queued agent task."
    return "Create a low-risk agent task or continue current mission execution."


def list_agent_tasks_filtered(status: str | None = None, risk_level: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    tasks = list_agent_tasks(limit=250)

    if status:
        tasks = [task for task in tasks if str(task.get("status") or "").lower() == status.lower()]

    if risk_level:
        tasks = [task for task in tasks if str(task.get("risk_level") or "").lower() == risk_level.lower()]

    return tasks[:limit]


def get_route_inventory(app: Any) -> list[dict[str, Any]]:
    routes: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()

    # Primary source: FastAPI/OpenAPI path registry.
    try:
        schema = app.openapi()
        paths = schema.get("paths", {}) if isinstance(schema, dict) else {}

        for route_path, operations in paths.items():
            if not isinstance(operations, dict):
                continue

            methods = sorted(
                method.upper()
                for method in operations.keys()
                if method.lower() in {"get", "post", "put", "patch", "delete", "head", "options"}
            )

            normalized_path = route_path.rstrip("/") if route_path != "/" else route_path
            key = (normalized_path, ",".join(methods))

            if key in seen:
                continue

            seen.add(key)
            routes.append(
                {
                    "path": normalized_path,
                    "methods": methods,
                    "name": "",
                    "is_api": normalized_path.startswith("/api/"),
                    "is_mission_control": "mission-control" in normalized_path,
                }
            )
    except Exception:
        pass

    # Fallback source: raw Starlette/FastAPI routes.
    app_routes = list(getattr(app, "routes", []) or [])
    router = getattr(app, "router", None)
    router_routes = list(getattr(router, "routes", []) or []) if router else []

    for route in app_routes + router_routes:
        route_path = (
            getattr(route, "path", "")
            or getattr(route, "path_format", "")
            or ""
        )
        methods = sorted(list(getattr(route, "methods", []) or []))
        name = getattr(route, "name", "") or ""

        if not route_path:
            continue

        normalized_path = route_path.rstrip("/") if route_path != "/" else route_path
        key = (normalized_path, ",".join(methods))

        if key in seen:
            continue

        seen.add(key)
        routes.append(
            {
                "path": normalized_path,
                "methods": methods,
                "name": name,
                "is_api": normalized_path.startswith("/api/"),
                "is_mission_control": "mission-control" in normalized_path,
            }
        )

    return sorted(routes, key=lambda item: item["path"])


def get_mission_control_contract(app: Any) -> dict[str, Any]:
    routes = get_route_inventory(app)
    mission_routes = [route for route in routes if route["is_mission_control"]]
    api_routes = [route for route in mission_routes if route["is_api"]]
    ui_routes = [route for route in mission_routes if not route["is_api"]]

    required_paths = [
        "/mission-control",
        "/mission-control/v1",
        "/mission-control/ui",
        "/api/mission-control/state",
        "/api/mission-control/readiness",
        "/api/mission-control/operator-queue",
        "/api/mission-control/agent/state",
        "/api/mission-control/agent/tasks",
        "/api/mission-control/agent/risk-dashboard",
        "/api/mission-control/snapshots",
        "/api/mission-control/mvp-readiness",
        "/api/mission-control/connectors",
        "/api/mission-control/agent-runtime",
        "/api/mission-control/firewall",
        "/api/mission-control/tool-adapters",
        "/api/mission-control/model-providers",
        "/api/mission-control/background-jobs",
        "/api/mission-control/auth/status",
        "/api/mission-control/export",
        "/api/mission-control/daily-loop",
        "/api/mission-control/records",
    ]

    present = {route["path"] for route in routes}
    missing = [path for path in required_paths if path not in present]

    return {
        "status": "ok" if not missing else "degraded",
        "required_paths": required_paths,
        "missing_paths": missing,
        "counts": {
            "total_routes": len(routes),
            "mission_control_routes": len(mission_routes),
            "mission_control_api_routes": len(api_routes),
            "mission_control_ui_routes": len(ui_routes),
        },
        "mission_control_routes": mission_routes,
    }


def get_system_health(app: Any) -> dict[str, Any]:
    contract = get_mission_control_contract(app)
    state = get_mission_control_state()
    agent_state = get_agent_execution_state()
    risk_dashboard = get_agent_risk_dashboard()

    checks = {
        "route_contract": contract["status"] == "ok",
        "mission_control_state": state.get("status") == "ok",
        "agent_execution_state": agent_state.get("status") == "ok",
        "risk_dashboard": risk_dashboard.get("status") == "ok",
        "storage": _storage_health_check(),
    }

    failed = [name for name, passed in checks.items() if not passed]

    if failed:
        posture = "degraded"
    elif risk_dashboard.get("posture") in {"elevated", "approval_required"}:
        posture = "attention_required"
    else:
        posture = "healthy"

    return {
        "status": "ok" if not failed else "degraded",
        "posture": posture,
        "checks": checks,
        "failed_checks": failed,
        "contract": contract,
        "mission_control_readiness": state.get("readiness", {}),
        "agent_counts": agent_state.get("counts", {}),
        "risk": {
            "posture": risk_dashboard.get("posture"),
            "by_risk": risk_dashboard.get("by_risk", {}),
            "recommended_action": risk_dashboard.get("recommended_action"),
        },
    }


def _storage_health_check() -> bool:
    try:
        with store.connect() as conn:
            store.ensure_tables(conn)
            conn.execute("SELECT 1").fetchone()
        return True
    except Exception:
        return False


def _snapshot_dir() -> Path:
    directory = Path("snapshots")
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def _snapshot_metadata_path(snapshot_name: str) -> Path:
    return _snapshot_dir() / f"{snapshot_name}.json"


def _snapshot_db_path(snapshot_name: str) -> Path:
    return _snapshot_dir() / f"{snapshot_name}.db"


def create_system_snapshot(label: str | None = None, actor: str = "commander") -> dict[str, Any]:
    import shutil
    import json

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    clean_label = "".join(
        char.lower() if char.isalnum() else "_"
        for char in str(label or "manual_snapshot")
    ).strip("_") or "manual_snapshot"

    snapshot_name = f"{timestamp}_{clean_label}"
    source_db = store.db_path()
    snapshot_db = _snapshot_db_path(snapshot_name)
    metadata_path = _snapshot_metadata_path(snapshot_name)

    with store.connect() as conn:
        store.ensure_tables(conn)
        conn.commit()

    if not source_db.exists():
        return {
            "status": "failed",
            "reason": "database_not_found",
            "source_db": str(source_db),
        }

    shutil.copy2(source_db, snapshot_db)

    health_summary = {
        "storage": _storage_health_check(),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    metadata = {
        "status": "created",
        "snapshot_name": snapshot_name,
        "label": label or "manual_snapshot",
        "actor": actor,
        "database_path": str(snapshot_db),
        "metadata_path": str(metadata_path),
        "source_db": str(source_db),
        "size_bytes": snapshot_db.stat().st_size if snapshot_db.exists() else 0,
        "health_summary": health_summary,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    metadata_path.write_text(json.dumps(metadata, indent=2))

    audit_log(
        actor=actor,
        action="system_snapshot_created",
        target_type="snapshot",
        target_id=snapshot_name,
        detail=f"Created system snapshot {snapshot_name}",
    )

    return metadata


def list_system_snapshots(limit: int = 50) -> list[dict[str, Any]]:
    import json

    snapshots = []

    for metadata_path in sorted(_snapshot_dir().glob("*.json"), reverse=True):
        try:
            metadata = json.loads(metadata_path.read_text())
        except Exception:
            metadata = {
                "status": "unreadable_metadata",
                "snapshot_name": metadata_path.stem,
                "metadata_path": str(metadata_path),
            }

        db_path = _snapshot_db_path(metadata_path.stem)
        metadata["database_exists"] = db_path.exists()
        metadata["metadata_exists"] = metadata_path.exists()
        metadata["size_bytes"] = db_path.stat().st_size if db_path.exists() else metadata.get("size_bytes", 0)
        snapshots.append(metadata)

    return snapshots[:limit]


def get_system_snapshot(snapshot_name: str) -> dict[str, Any] | None:
    import json

    safe_name = Path(snapshot_name).name
    metadata_path = _snapshot_metadata_path(safe_name)

    if not metadata_path.exists():
        return None

    try:
        metadata = json.loads(metadata_path.read_text())
    except Exception:
        metadata = {
            "status": "unreadable_metadata",
            "snapshot_name": safe_name,
            "metadata_path": str(metadata_path),
        }

    db_path = _snapshot_db_path(safe_name)
    metadata["database_exists"] = db_path.exists()
    metadata["metadata_exists"] = metadata_path.exists()
    metadata["size_bytes"] = db_path.stat().st_size if db_path.exists() else metadata.get("size_bytes", 0)

    return metadata


def restore_system_snapshot(snapshot_name: str, actor: str = "commander") -> dict[str, Any]:
    import shutil

    safe_name = Path(snapshot_name).name
    snapshot_db = _snapshot_db_path(safe_name)
    target_db = store.db_path()

    if not snapshot_db.exists():
        return {
            "status": "not_found",
            "snapshot_name": safe_name,
            "reason": "snapshot_database_missing",
        }

    pre_restore = create_system_snapshot(
        label=f"pre_restore_{safe_name}",
        actor=actor,
    )

    shutil.copy2(snapshot_db, target_db)

    audit_log(
        actor=actor,
        action="system_snapshot_restored",
        target_type="snapshot",
        target_id=safe_name,
        detail=f"Restored snapshot {safe_name}; pre-restore backup {pre_restore.get('snapshot_name')}",
    )

    return {
        "status": "restored",
        "snapshot_name": safe_name,
        "target_db": str(target_db),
        "pre_restore_snapshot": pre_restore.get("snapshot_name"),
        "restored_at": datetime.now(timezone.utc).isoformat(),
    }


def delete_system_snapshot(snapshot_name: str, actor: str = "commander") -> dict[str, Any]:
    safe_name = Path(snapshot_name).name
    db_path = _snapshot_db_path(safe_name)
    metadata_path = _snapshot_metadata_path(safe_name)

    removed = []

    if db_path.exists():
        db_path.unlink()
        removed.append(str(db_path))

    if metadata_path.exists():
        metadata_path.unlink()
        removed.append(str(metadata_path))

    if removed:
        audit_log(
            actor=actor,
            action="system_snapshot_deleted",
            target_type="snapshot",
            target_id=safe_name,
            detail=f"Deleted snapshot files: {removed}",
        )

    return {
        "status": "deleted" if removed else "not_found",
        "snapshot_name": safe_name,
        "removed": removed,
    }


def get_snapshot_system_state() -> dict[str, Any]:
    snapshots = list_system_snapshots()

    latest = snapshots[0] if snapshots else None

    return {
        "status": "ok",
        "snapshot_count": len(snapshots),
        "latest_snapshot": latest,
        "snapshots": snapshots,
        "snapshot_directory": str(_snapshot_dir()),
        "recommended_action": (
            "Create a fresh system snapshot before the next major build."
            if not snapshots
            else "Snapshot protection active. Create another snapshot before risky schema changes."
        ),
    }


def ensure_memory_records_tables() -> None:
    with store.connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                record_type TEXT NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                source TEXT NOT NULL,
                tags TEXT,
                linked_mission_id TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_daily_loop (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                loop_type TEXT NOT NULL,
                status TEXT NOT NULL,
                summary TEXT NOT NULL,
                recommended_action TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.commit()


def create_record_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    ensure_memory_records_tables()
    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO mission_control_records
            (record_type, title, content, source, tags, linked_mission_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.get("record_type") or "note",
                payload.get("title") or "Untitled Record",
                payload.get("content") or "",
                payload.get("source") or "commander",
                payload.get("tags") or "",
                str(payload.get("linked_mission_id") or ""),
                now,
            ),
        )
        record_id = cursor.lastrowid
        conn.commit()

    audit_log(
        actor=payload.get("source") or "commander",
        action="record_created",
        target_type="record",
        target_id=str(record_id),
        detail=f"Created record: {payload.get('title') or 'Untitled Record'}",
    )

    return get_record(record_id) or {"id": record_id, "status": "created"}


def get_record(record_id: int) -> dict[str, Any] | None:
    ensure_memory_records_tables()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        row = conn.execute(
            "SELECT * FROM mission_control_records WHERE id = ?",
            (record_id,),
        ).fetchone()

    return dict(row) if row else None


def list_records(limit: int = 100) -> list[dict[str, Any]]:
    ensure_memory_records_tables()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        rows = conn.execute(
            "SELECT * FROM mission_control_records ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def create_daily_loop(loop_type: str = "full_cycle", actor: str = "commander") -> dict[str, Any]:
    ensure_memory_records_tables()

    state = get_mission_control_state()
    agent_state = get_agent_execution_state()
    risk = get_agent_risk_dashboard()
    snapshots = get_snapshot_system_state()

    active_missions = state.get("active_missions", [])
    readiness = state.get("readiness", {})
    agent_counts = agent_state.get("counts", {})

    summary = (
        f"Loop={loop_type}; active_missions={len(active_missions)}; "
        f"readiness={readiness}; agent_counts={agent_counts}; "
        f"risk_posture={risk.get('posture')}; snapshots={snapshots.get('snapshot_count')}"
    )

    recommended_action = (
        risk.get("recommended_action")
        or readiness.get("recommended_action")
        or "Execute highest-priority active mission and capture AAR."
    )

    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO mission_control_daily_loop
            (loop_type, status, summary, recommended_action, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                loop_type,
                "generated",
                summary,
                recommended_action,
                now,
            ),
        )
        loop_id = cursor.lastrowid
        conn.commit()

    audit_log(
        actor=actor,
        action="daily_loop_generated",
        target_type="daily_loop",
        target_id=str(loop_id),
        detail=f"Generated daily loop: {loop_type}",
    )

    return get_daily_loop(loop_id) or {"id": loop_id, "status": "generated"}


def get_daily_loop(loop_id: int) -> dict[str, Any] | None:
    ensure_memory_records_tables()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        row = conn.execute(
            "SELECT * FROM mission_control_daily_loop WHERE id = ?",
            (loop_id,),
        ).fetchone()

    return dict(row) if row else None


def list_daily_loops(limit: int = 50) -> list[dict[str, Any]]:
    ensure_memory_records_tables()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        rows = conn.execute(
            "SELECT * FROM mission_control_daily_loop ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def export_command_state() -> dict[str, Any]:
    ensure_memory_records_tables()

    return {
        "status": "ok",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "mission_control": get_mission_control_state(),
        "agent_execution": get_agent_execution_state(),
        "agent_risk": get_agent_risk_dashboard(),
        "system_health": {
            "storage": _storage_health_check(),
            "snapshots": get_snapshot_system_state(),
        },
        "records": list_records(100),
        "daily_loops": list_daily_loops(50),
        "connectors": get_connector_registry_state(),
        "agent_runtime": get_agent_runtime_state(),
        "external_action_firewall": get_external_action_firewall_state(),
        "tool_adapters": get_tool_adapter_state(),
        "model_providers": get_model_provider_state(),
        "background_jobs": get_background_job_state(),
        "local_auth": get_local_auth_state(),
        "audit_log": list_audit_log(100),
    }


def get_local_mvp_readiness() -> dict[str, Any]:
    checks = {
        "mission_control_state": get_mission_control_state().get("status") == "ok",
        "agent_execution": get_agent_execution_state().get("status") == "ok",
        "risk_dashboard": get_agent_risk_dashboard().get("status") == "ok",
        "snapshots": get_snapshot_system_state().get("status") == "ok",
        "records": isinstance(list_records(10), list),
        "daily_loop": isinstance(list_daily_loops(10), list),
        "connectors": get_connector_registry_state().get("status") == "ok",
        "agent_runtime": get_agent_runtime_state().get("status") == "ok",
        "external_action_firewall": get_external_action_firewall_state().get("status") == "ok",
        "tool_adapters": get_tool_adapter_state().get("status") == "ok",
        "model_providers": get_model_provider_state().get("status") == "ok",
        "background_jobs": get_background_job_state().get("status") == "ok",
        "local_auth": get_local_auth_state().get("status") == "ok",
        "storage": _storage_health_check(),
    }

    failed = [name for name, passed in checks.items() if not passed]

    if failed:
        status = "degraded"
        recommendation = "Fix failed MVP checks before adding more features."
    else:
        status = "ready"
        recommendation = "Local MVP foundation is ready for daily use and next-stage connector work."

    return {
        "status": status,
        "checks": checks,
        "failed_checks": failed,
        "recommended_action": recommendation,
    }


def ensure_connector_tables() -> None:
    with store.connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_connectors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                connector_key TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                connector_type TEXT NOT NULL,
                status TEXT NOT NULL,
                permission_level TEXT NOT NULL,
                enabled INTEGER NOT NULL,
                config_summary TEXT,
                last_health_check TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_connector_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                connector_key TEXT NOT NULL,
                event_type TEXT NOT NULL,
                status TEXT NOT NULL,
                detail TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.commit()


def seed_default_connectors() -> None:
    ensure_connector_tables()
    now = datetime.now(timezone.utc).isoformat()

    defaults = [
        {
            "connector_key": "gmail",
            "name": "Gmail",
            "connector_type": "email",
            "status": "not_connected",
            "permission_level": "external_read",
            "enabled": 0,
            "config_summary": "Future connector for email search, reading, drafting, and commander-approved sending.",
        },
        {
            "connector_key": "google_calendar",
            "name": "Google Calendar",
            "connector_type": "calendar",
            "status": "not_connected",
            "permission_level": "external_read_write",
            "enabled": 0,
            "config_summary": "Future connector for schedule visibility, availability, and approved event creation.",
        },
        {
            "connector_key": "files",
            "name": "Files / Documents",
            "connector_type": "files",
            "status": "local_ready",
            "permission_level": "local_read_write",
            "enabled": 1,
            "config_summary": "Local file and document reference layer.",
        },
        {
            "connector_key": "finance",
            "name": "Finance Data",
            "connector_type": "finance",
            "status": "not_connected",
            "permission_level": "sensitive_read",
            "enabled": 0,
            "config_summary": "Future connector for personal finance, spending, subscriptions, and portfolio views.",
        },
        {
            "connector_key": "webhooks",
            "name": "Webhooks",
            "connector_type": "api",
            "status": "not_configured",
            "permission_level": "external_receive",
            "enabled": 0,
            "config_summary": "Future inbound/outbound webhook bridge for external systems.",
        },
        {
            "connector_key": "model_providers",
            "name": "Model Providers",
            "connector_type": "ai_model",
            "status": "planned",
            "permission_level": "model_runtime",
            "enabled": 0,
            "config_summary": "Future abstraction for OpenAI, local models, and fallback providers.",
        },
    ]

    with store.connect() as conn:
        for connector in defaults:
            conn.execute(
                """
                INSERT OR IGNORE INTO mission_control_connectors
                (
                    connector_key, name, connector_type, status, permission_level,
                    enabled, config_summary, last_health_check, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    connector["connector_key"],
                    connector["name"],
                    connector["connector_type"],
                    connector["status"],
                    connector["permission_level"],
                    connector["enabled"],
                    connector["config_summary"],
                    None,
                    now,
                    now,
                ),
            )

        conn.commit()


def list_connectors(limit: int = 100) -> list[dict[str, Any]]:
    seed_default_connectors()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        rows = conn.execute(
            "SELECT * FROM mission_control_connectors ORDER BY id ASC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_connector(connector_key: str) -> dict[str, Any] | None:
    seed_default_connectors()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        row = conn.execute(
            "SELECT * FROM mission_control_connectors WHERE connector_key = ?",
            (connector_key,),
        ).fetchone()

    return dict(row) if row else None


def upsert_connector_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    ensure_connector_tables()

    connector_key = str(payload.get("connector_key") or "").strip().lower().replace(" ", "_")
    if not connector_key:
        return {"status": "failed", "reason": "connector_key_required"}

    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        conn.execute(
            """
            INSERT INTO mission_control_connectors
            (
                connector_key, name, connector_type, status, permission_level,
                enabled, config_summary, last_health_check, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(connector_key) DO UPDATE SET
                name = excluded.name,
                connector_type = excluded.connector_type,
                status = excluded.status,
                permission_level = excluded.permission_level,
                enabled = excluded.enabled,
                config_summary = excluded.config_summary,
                updated_at = excluded.updated_at
            """,
            (
                connector_key,
                payload.get("name") or connector_key,
                payload.get("connector_type") or "generic",
                payload.get("status") or "planned",
                payload.get("permission_level") or "external_read",
                1 if payload.get("enabled") in {True, 1, "1", "true", "yes", "on"} else 0,
                payload.get("config_summary") or "",
                None,
                now,
                now,
            ),
        )
        conn.commit()

    audit_log(
        actor=payload.get("actor") or "commander",
        action="connector_upserted",
        target_type="connector",
        target_id=connector_key,
        detail=f"Connector {connector_key} upserted.",
    )

    return get_connector(connector_key) or {"status": "failed", "reason": "connector_not_found_after_upsert"}


def update_connector_status(connector_key: str, status: str, detail: str = "", actor: str = "system") -> dict[str, Any]:
    ensure_connector_tables()

    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        row = conn.execute(
            "SELECT id FROM mission_control_connectors WHERE connector_key = ?",
            (connector_key,),
        ).fetchone()

        if row is None:
            return {"status": "not_found", "connector_key": connector_key}

        conn.execute(
            """
            UPDATE mission_control_connectors
            SET status = ?, last_health_check = ?, updated_at = ?
            WHERE connector_key = ?
            """,
            (status, now, now, connector_key),
        )

        conn.execute(
            """
            INSERT INTO mission_control_connector_events
            (connector_key, event_type, status, detail, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                connector_key,
                "status_update",
                status,
                detail or f"Connector status updated to {status}.",
                now,
            ),
        )

        conn.commit()

    audit_log(
        actor=actor,
        action="connector_status_updated",
        target_type="connector",
        target_id=connector_key,
        detail=detail or f"Connector status updated to {status}.",
    )

    return get_connector(connector_key) or {"status": "not_found", "connector_key": connector_key}


def set_connector_enabled(connector_key: str, enabled: bool, actor: str = "commander") -> dict[str, Any]:
    ensure_connector_tables()

    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        row = conn.execute(
            "SELECT id FROM mission_control_connectors WHERE connector_key = ?",
            (connector_key,),
        ).fetchone()

        if row is None:
            return {"status": "not_found", "connector_key": connector_key}

        conn.execute(
            """
            UPDATE mission_control_connectors
            SET enabled = ?, updated_at = ?
            WHERE connector_key = ?
            """,
            (1 if enabled else 0, now, connector_key),
        )

        conn.execute(
            """
            INSERT INTO mission_control_connector_events
            (connector_key, event_type, status, detail, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                connector_key,
                "enabled_changed",
                "enabled" if enabled else "disabled",
                f"Connector enabled={enabled}",
                now,
            ),
        )

        conn.commit()

    audit_log(
        actor=actor,
        action="connector_enabled_changed",
        target_type="connector",
        target_id=connector_key,
        detail=f"Connector enabled={enabled}",
    )

    return get_connector(connector_key) or {"status": "not_found", "connector_key": connector_key}


def list_connector_events(limit: int = 100) -> list[dict[str, Any]]:
    ensure_connector_tables()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        rows = conn.execute(
            "SELECT * FROM mission_control_connector_events ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_connector_registry_state() -> dict[str, Any]:
    connectors = list_connectors()
    events = list_connector_events(50)

    enabled = [connector for connector in connectors if int(connector.get("enabled") or 0) == 1]
    connected = [
        connector for connector in connectors
        if str(connector.get("status") or "").lower() in {"connected", "ready", "local_ready"}
    ]
    sensitive = [
        connector for connector in connectors
        if str(connector.get("permission_level") or "").lower() in {"sensitive_read", "external_read_write", "external_send"}
    ]

    return {
        "status": "ok",
        "counts": {
            "total": len(connectors),
            "enabled": len(enabled),
            "connected_or_ready": len(connected),
            "sensitive": len(sensitive),
            "events": len(events),
        },
        "connectors": connectors,
        "events": events,
        "recommended_action": (
            "Connector registry ready. Enable only one connector at a time with explicit permission gates."
            if connectors
            else "Seed default connectors."
        ),
    }


def ensure_agent_runtime_tables() -> None:
    ensure_agent_execution_tables()

    with store.connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_agent_runtime_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                actor TEXT NOT NULL,
                event_type TEXT NOT NULL,
                status TEXT NOT NULL,
                detail TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.commit()


def record_agent_runtime_event(
    task_id: int,
    actor: str,
    event_type: str,
    status: str,
    detail: str,
) -> dict[str, Any]:
    ensure_agent_runtime_tables()
    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO mission_control_agent_runtime_events
            (task_id, actor, event_type, status, detail, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                task_id,
                actor or "agent_runtime",
                event_type or "runtime_event",
                status or "unknown",
                detail or "",
                now,
            ),
        )
        event_id = cursor.lastrowid
        conn.commit()

    return {
        "id": event_id,
        "task_id": task_id,
        "actor": actor,
        "event_type": event_type,
        "status": status,
        "detail": detail,
        "created_at": now,
    }


def list_agent_runtime_events(limit: int = 100) -> list[dict[str, Any]]:
    ensure_agent_runtime_tables()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        rows = conn.execute(
            """
            SELECT * FROM mission_control_agent_runtime_events
            ORDER BY id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def _runtime_can_execute(task: dict[str, Any]) -> tuple[bool, str]:
    status = str(task.get("status") or "").lower()

    if status not in {"queued", "approved"}:
        return False, f"Task status is not executable: {status}"

    if int(task.get("requires_approval") or 0) == 1 and int(task.get("approved") or 0) != 1:
        return False, "Task requires commander approval."

    risk = str(task.get("risk_level") or "medium").lower()
    if risk == "critical":
        return False, "Critical-risk tasks are blocked from automatic runtime execution."

    return True, "Task is executable."


def start_agent_task_runtime(task_id: int, actor: str = "agent_runtime") -> dict[str, Any]:
    ensure_agent_runtime_tables()
    task = get_agent_task(task_id)

    if not task:
        return {"status": "not_found", "task_id": task_id}

    can_execute, reason = _runtime_can_execute(task)

    if not can_execute:
        record_agent_runtime_event(
            task_id=task_id,
            actor=actor,
            event_type="runtime_blocked",
            status="blocked",
            detail=reason,
        )
        audit_log(
            actor=actor,
            action="agent_runtime_blocked",
            target_type="agent_task",
            target_id=str(task_id),
            detail=reason,
        )
        return {
            "status": "blocked",
            "task_id": task_id,
            "reason": reason,
        }

    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        conn.execute(
            """
            UPDATE mission_control_agent_tasks
            SET status = ?, updated_at = ?
            WHERE id = ? AND status IN ('queued', 'approved')
            """,
            ("running", now, task_id),
        )
        conn.commit()

    record_agent_runtime_event(
        task_id=task_id,
        actor=actor,
        event_type="runtime_started",
        status="running",
        detail="Agent runtime started task.",
    )

    audit_log(
        actor=actor,
        action="agent_runtime_started",
        target_type="agent_task",
        target_id=str(task_id),
        detail="Agent runtime started local task execution.",
    )

    return {
        "status": "running",
        "task_id": task_id,
    }


def finish_agent_task_runtime(
    task_id: int,
    result: dict[str, Any] | None = None,
    actor: str = "agent_runtime",
    final_status: str = "completed",
) -> dict[str, Any]:
    import json

    ensure_agent_runtime_tables()

    task = get_agent_task(task_id)
    if not task:
        return {"status": "not_found", "task_id": task_id}

    allowed_final = {"completed", "failed", "blocked"}
    if final_status not in allowed_final:
        final_status = "completed"

    now = datetime.now(timezone.utc).isoformat()
    result_payload = result or {"message": f"Task {final_status} by local runtime."}

    with store.connect() as conn:
        conn.execute(
            """
            UPDATE mission_control_agent_tasks
            SET status = ?, result = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                final_status,
                json.dumps(result_payload),
                now,
                task_id,
            ),
        )
        conn.commit()

    record_agent_runtime_event(
        task_id=task_id,
        actor=actor,
        event_type=f"runtime_{final_status}",
        status=final_status,
        detail=json.dumps(result_payload),
    )

    audit_log(
        actor=actor,
        action=f"agent_runtime_{final_status}",
        target_type="agent_task",
        target_id=str(task_id),
        detail=f"Agent runtime marked task {final_status}.",
    )

    return {
        "status": final_status,
        "task_id": task_id,
        "result": result_payload,
    }


def run_agent_task_once(task_id: int, actor: str = "agent_runtime") -> dict[str, Any]:
    start = start_agent_task_runtime(task_id, actor=actor)

    if start.get("status") != "running":
        return start

    task = get_agent_task(task_id) or {}

    simulated_result = {
        "message": "Local runtime executed task placeholder.",
        "task_id": task_id,
        "title": task.get("title"),
        "task_type": task.get("task_type"),
        "source": task.get("source"),
        "next_stage": "Connect real tool adapters in the connector execution layer.",
    }

    return finish_agent_task_runtime(
        task_id=task_id,
        result=simulated_result,
        actor=actor,
        final_status="completed",
    )


def run_next_agent_task(actor: str = "agent_runtime") -> dict[str, Any]:
    ensure_agent_runtime_tables()

    queued = list_agent_tasks_filtered(status="queued", limit=25)

    for task in queued:
        task_id = int(task.get("id"))
        can_execute, _reason = _runtime_can_execute(task)
        if can_execute:
            return run_agent_task_once(task_id, actor=actor)

    return {
        "status": "idle",
        "reason": "No executable queued agent tasks.",
    }


def run_agent_runtime_batch(limit: int = 5, actor: str = "agent_runtime") -> dict[str, Any]:
    results = []

    for _ in range(max(1, min(limit, 20))):
        result = run_next_agent_task(actor=actor)
        results.append(result)

        if result.get("status") == "idle":
            break

    completed = [result for result in results if result.get("status") == "completed"]
    blocked = [result for result in results if result.get("status") == "blocked"]

    return {
        "status": "ok",
        "attempted": len(results),
        "completed": len(completed),
        "blocked": len(blocked),
        "results": results,
    }


def get_agent_runtime_state() -> dict[str, Any]:
    ensure_agent_runtime_tables()

    tasks = list_agent_tasks(250)
    events = list_agent_runtime_events(100)

    running = [task for task in tasks if str(task.get("status") or "").lower() == "running"]
    queued = [task for task in tasks if str(task.get("status") or "").lower() == "queued"]
    completed = [task for task in tasks if str(task.get("status") or "").lower() == "completed"]
    failed = [task for task in tasks if str(task.get("status") or "").lower() == "failed"]
    blocked = [task for task in tasks if str(task.get("status") or "").lower() == "blocked"]

    return {
        "status": "ok",
        "counts": {
            "running": len(running),
            "queued": len(queued),
            "completed": len(completed),
            "failed": len(failed),
            "blocked": len(blocked),
            "runtime_events": len(events),
        },
        "running": running[:25],
        "queued": queued[:25],
        "latest_events": events[:25],
        "recommended_action": (
            "Run next queued task."
            if queued
            else "Create or approve agent tasks before running the runtime."
        ),
    }


def ensure_external_action_tables() -> None:
    with store.connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_external_actions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                connector_key TEXT NOT NULL,
                action_type TEXT NOT NULL,
                title TEXT NOT NULL,
                payload TEXT NOT NULL,
                risk_level TEXT NOT NULL,
                status TEXT NOT NULL,
                requested_by TEXT NOT NULL,
                approved_by TEXT,
                rejection_reason TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_external_action_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                actor TEXT NOT NULL,
                status TEXT NOT NULL,
                detail TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.commit()


def classify_external_action(connector_key: str, action_type: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = payload or {}
    connector = str(connector_key or "").lower()
    action = str(action_type or "").lower()

    critical_terms = {"send_money", "trade", "delete_account", "credential_change", "wire", "payment"}
    high_terms = {"send_email", "create_event", "delete", "external_write", "post_webhook", "modify_file"}
    medium_terms = {"draft_email", "read_email", "read_calendar", "read_finance", "summarize_file"}
    low_terms = {
        "read_local",
        "summarize_local",
        "status_check",
        "list",
        "list_project_files",
        "read_project_file",
        "summarize_project_file",
    }

    if action in critical_terms or connector == "finance" and action not in {"read_finance", "status_check"}:
        risk = "critical"
        requires_approval = True
        blocked_from_auto_execute = True
        reason = "Critical external action requires explicit commander approval and cannot auto-execute."
    elif action in high_terms:
        risk = "high"
        requires_approval = True
        blocked_from_auto_execute = False
        reason = "High-risk external action requires approval before execution."
    elif action in medium_terms or connector in {"gmail", "google_calendar", "finance"}:
        risk = "medium"
        requires_approval = True
        blocked_from_auto_execute = False
        reason = "Sensitive connector action requires approval."
    elif action in low_terms:
        risk = "low"
        requires_approval = False
        blocked_from_auto_execute = False
        reason = "Low-risk local/read action may proceed."
    else:
        risk = "medium"
        requires_approval = True
        blocked_from_auto_execute = False
        reason = "Unknown action defaults to approval required."

    return {
        "status": "classified",
        "connector_key": connector_key,
        "action_type": action_type,
        "risk_level": risk,
        "requires_approval": requires_approval,
        "blocked_from_auto_execute": blocked_from_auto_execute,
        "reason": reason,
    }


def record_external_action_event(
    action_id: int,
    event_type: str,
    actor: str,
    status: str,
    detail: str,
) -> dict[str, Any]:
    ensure_external_action_tables()
    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO mission_control_external_action_events
            (action_id, event_type, actor, status, detail, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                action_id,
                event_type or "external_action_event",
                actor or "system",
                status or "unknown",
                detail or "",
                now,
            ),
        )
        event_id = cursor.lastrowid
        conn.commit()

    return {
        "id": event_id,
        "action_id": action_id,
        "event_type": event_type,
        "actor": actor,
        "status": status,
        "detail": detail,
        "created_at": now,
    }


def create_external_action_request(payload: dict[str, Any]) -> dict[str, Any]:
    import json

    ensure_external_action_tables()

    connector_key = payload.get("connector_key") or "unknown"
    action_type = payload.get("action_type") or "unknown_action"
    classification = classify_external_action(
        connector_key=connector_key,
        action_type=action_type,
        payload=payload.get("payload") or {},
    )

    status = "pending_approval" if classification["requires_approval"] else "approved"
    if classification["blocked_from_auto_execute"]:
        status = "pending_approval"

    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO mission_control_external_actions
            (
                connector_key, action_type, title, payload, risk_level,
                status, requested_by, approved_by, rejection_reason,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                connector_key,
                action_type,
                payload.get("title") or f"{connector_key}:{action_type}",
                json.dumps(payload.get("payload") or payload),
                classification["risk_level"],
                status,
                payload.get("requested_by") or "agent_runtime",
                None,
                None,
                now,
                now,
            ),
        )
        action_id = cursor.lastrowid
        conn.commit()

    record_external_action_event(
        action_id=action_id,
        event_type="requested",
        actor=payload.get("requested_by") or "agent_runtime",
        status=status,
        detail=classification["reason"],
    )

    audit_log(
        actor=payload.get("requested_by") or "agent_runtime",
        action="external_action_requested",
        target_type="external_action",
        target_id=str(action_id),
        detail=f"{connector_key}:{action_type} classified as {classification['risk_level']}",
    )

    return get_external_action(action_id) or {"id": action_id, "status": status}


def get_external_action(action_id: int) -> dict[str, Any] | None:
    ensure_external_action_tables()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        row = conn.execute(
            "SELECT * FROM mission_control_external_actions WHERE id = ?",
            (action_id,),
        ).fetchone()

    return dict(row) if row else None


def list_external_actions(limit: int = 100) -> list[dict[str, Any]]:
    ensure_external_action_tables()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        rows = conn.execute(
            "SELECT * FROM mission_control_external_actions ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def list_external_action_events(limit: int = 100) -> list[dict[str, Any]]:
    ensure_external_action_tables()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        rows = conn.execute(
            "SELECT * FROM mission_control_external_action_events ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def approve_external_action(action_id: int, actor: str = "commander") -> dict[str, Any]:
    ensure_external_action_tables()
    action = get_external_action(action_id)

    if not action:
        return {"status": "not_found", "action_id": action_id}

    classification = classify_external_action(
        connector_key=action.get("connector_key"),
        action_type=action.get("action_type"),
        payload={},
    )

    status = "approved"
    if classification.get("blocked_from_auto_execute"):
        status = "approved_manual_only"

    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        conn.execute(
            """
            UPDATE mission_control_external_actions
            SET status = ?, approved_by = ?, updated_at = ?
            WHERE id = ?
            """,
            (status, actor, now, action_id),
        )
        conn.commit()

    record_external_action_event(
        action_id=action_id,
        event_type="approved",
        actor=actor,
        status=status,
        detail=classification["reason"],
    )

    audit_log(
        actor=actor,
        action="external_action_approved",
        target_type="external_action",
        target_id=str(action_id),
        detail=f"External action approved with status={status}.",
    )

    return get_external_action(action_id) or {"status": status, "action_id": action_id}


def reject_external_action(action_id: int, reason: str = "", actor: str = "commander") -> dict[str, Any]:
    ensure_external_action_tables()

    if not get_external_action(action_id):
        return {"status": "not_found", "action_id": action_id}

    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        conn.execute(
            """
            UPDATE mission_control_external_actions
            SET status = ?, rejection_reason = ?, updated_at = ?
            WHERE id = ?
            """,
            ("rejected", reason or "Rejected by commander.", now, action_id),
        )
        conn.commit()

    record_external_action_event(
        action_id=action_id,
        event_type="rejected",
        actor=actor,
        status="rejected",
        detail=reason or "Rejected by commander.",
    )

    audit_log(
        actor=actor,
        action="external_action_rejected",
        target_type="external_action",
        target_id=str(action_id),
        detail=reason or "Rejected by commander.",
    )

    return get_external_action(action_id) or {"status": "rejected", "action_id": action_id}


def execute_external_action_placeholder(action_id: int, actor: str = "external_action_firewall") -> dict[str, Any]:
    action = get_external_action(action_id)

    if not action:
        return {"status": "not_found", "action_id": action_id}

    current_status = str(action.get("status") or "").lower()

    if current_status not in {"approved"}:
        record_external_action_event(
            action_id=action_id,
            event_type="execution_blocked",
            actor=actor,
            status="blocked",
            detail=f"Action status {current_status} is not executable.",
        )
        return {
            "status": "blocked",
            "reason": f"Action status {current_status} is not executable.",
            "action_id": action_id,
        }

    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        conn.execute(
            """
            UPDATE mission_control_external_actions
            SET status = ?, updated_at = ?
            WHERE id = ?
            """,
            ("executed_placeholder", now, action_id),
        )
        conn.commit()

    record_external_action_event(
        action_id=action_id,
        event_type="executed_placeholder",
        actor=actor,
        status="executed_placeholder",
        detail="Placeholder execution recorded. Real connector adapter not attached yet.",
    )

    audit_log(
        actor=actor,
        action="external_action_executed_placeholder",
        target_type="external_action",
        target_id=str(action_id),
        detail="Placeholder execution only. No external system changed.",
    )

    return {
        "status": "executed_placeholder",
        "action_id": action_id,
        "message": "No external system changed. Connector adapter not attached yet.",
    }


def get_external_action_firewall_state() -> dict[str, Any]:
    actions = list_external_actions(250)
    events = list_external_action_events(100)

    pending = [a for a in actions if str(a.get("status") or "").lower() == "pending_approval"]
    approved = [a for a in actions if str(a.get("status") or "").lower() == "approved"]
    manual_only = [a for a in actions if str(a.get("status") or "").lower() == "approved_manual_only"]
    rejected = [a for a in actions if str(a.get("status") or "").lower() == "rejected"]
    critical = [a for a in actions if str(a.get("risk_level") or "").lower() == "critical"]
    high = [a for a in actions if str(a.get("risk_level") or "").lower() == "high"]

    posture = "clear"
    if critical or manual_only:
        posture = "manual_review_required"
    elif pending:
        posture = "approval_required"
    elif high:
        posture = "elevated"

    return {
        "status": "ok",
        "posture": posture,
        "counts": {
            "total": len(actions),
            "pending_approval": len(pending),
            "approved": len(approved),
            "manual_only": len(manual_only),
            "rejected": len(rejected),
            "critical": len(critical),
            "high": len(high),
            "events": len(events),
        },
        "actions": actions,
        "events": events,
        "recommended_action": (
            "Review manual-only or critical external actions."
            if posture == "manual_review_required"
            else "Approve or reject pending external actions."
            if posture == "approval_required"
            else "External action firewall is clear."
        ),
    }


def ensure_tool_adapter_tables() -> None:
    with store.connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_tool_adapters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                adapter_key TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                adapter_type TEXT NOT NULL,
                connector_key TEXT NOT NULL,
                status TEXT NOT NULL,
                enabled INTEGER NOT NULL,
                allowed_actions TEXT NOT NULL,
                permission_level TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_tool_adapter_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                adapter_key TEXT NOT NULL,
                action_name TEXT NOT NULL,
                payload TEXT NOT NULL,
                status TEXT NOT NULL,
                result TEXT NOT NULL,
                firewall_action_id TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.commit()


def seed_default_tool_adapters() -> None:
    ensure_tool_adapter_tables()
    now = datetime.now(timezone.utc).isoformat()

    defaults = [
        {
            "adapter_key": "local_files",
            "name": "Local File Adapter",
            "adapter_type": "local_file",
            "connector_key": "files",
            "status": "ready",
            "enabled": 1,
            "allowed_actions": "list_project_files,read_project_file,summarize_project_file",
            "permission_level": "local_read",
            "description": "Safe local adapter for listing and reading project files inside the local repo boundary.",
        },
        {
            "adapter_key": "gmail_adapter",
            "name": "Gmail Adapter",
            "adapter_type": "email",
            "connector_key": "gmail",
            "status": "planned",
            "enabled": 0,
            "allowed_actions": "search_email,read_email,draft_email",
            "permission_level": "external_read_write",
            "description": "Planned Gmail adapter. External execution will require firewall approval.",
        },
        {
            "adapter_key": "calendar_adapter",
            "name": "Calendar Adapter",
            "adapter_type": "calendar",
            "connector_key": "google_calendar",
            "status": "planned",
            "enabled": 0,
            "allowed_actions": "read_calendar,create_event",
            "permission_level": "external_read_write",
            "description": "Planned calendar adapter. Write actions require firewall approval.",
        },
    ]

    with store.connect() as conn:
        for adapter in defaults:
            conn.execute(
                """
                INSERT OR IGNORE INTO mission_control_tool_adapters
                (
                    adapter_key, name, adapter_type, connector_key, status,
                    enabled, allowed_actions, permission_level, description,
                    created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    adapter["adapter_key"],
                    adapter["name"],
                    adapter["adapter_type"],
                    adapter["connector_key"],
                    adapter["status"],
                    adapter["enabled"],
                    adapter["allowed_actions"],
                    adapter["permission_level"],
                    adapter["description"],
                    now,
                    now,
                ),
            )

        conn.commit()


def list_tool_adapters(limit: int = 100) -> list[dict[str, Any]]:
    seed_default_tool_adapters()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        rows = conn.execute(
            "SELECT * FROM mission_control_tool_adapters ORDER BY id ASC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_tool_adapter(adapter_key: str) -> dict[str, Any] | None:
    seed_default_tool_adapters()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        row = conn.execute(
            "SELECT * FROM mission_control_tool_adapters WHERE adapter_key = ?",
            (adapter_key,),
        ).fetchone()

    return dict(row) if row else None


def upsert_tool_adapter_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    ensure_tool_adapter_tables()

    adapter_key = str(payload.get("adapter_key") or "").strip().lower().replace(" ", "_")
    if not adapter_key:
        return {"status": "failed", "reason": "adapter_key_required"}

    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        conn.execute(
            """
            INSERT INTO mission_control_tool_adapters
            (
                adapter_key, name, adapter_type, connector_key, status,
                enabled, allowed_actions, permission_level, description,
                created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(adapter_key) DO UPDATE SET
                name = excluded.name,
                adapter_type = excluded.adapter_type,
                connector_key = excluded.connector_key,
                status = excluded.status,
                enabled = excluded.enabled,
                allowed_actions = excluded.allowed_actions,
                permission_level = excluded.permission_level,
                description = excluded.description,
                updated_at = excluded.updated_at
            """,
            (
                adapter_key,
                payload.get("name") or adapter_key,
                payload.get("adapter_type") or "generic",
                payload.get("connector_key") or "unknown",
                payload.get("status") or "planned",
                1 if payload.get("enabled") in {True, 1, "1", "true", "yes", "on"} else 0,
                payload.get("allowed_actions") or "",
                payload.get("permission_level") or "external_read",
                payload.get("description") or "",
                now,
                now,
            ),
        )
        conn.commit()

    audit_log(
        actor=payload.get("actor") or "commander",
        action="tool_adapter_upserted",
        target_type="tool_adapter",
        target_id=adapter_key,
        detail=f"Tool adapter {adapter_key} saved.",
    )

    return get_tool_adapter(adapter_key) or {"status": "failed", "reason": "adapter_not_found_after_upsert"}


def set_tool_adapter_enabled(adapter_key: str, enabled: bool, actor: str = "commander") -> dict[str, Any]:
    ensure_tool_adapter_tables()
    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        row = conn.execute(
            "SELECT id FROM mission_control_tool_adapters WHERE adapter_key = ?",
            (adapter_key,),
        ).fetchone()

        if row is None:
            return {"status": "not_found", "adapter_key": adapter_key}

        conn.execute(
            """
            UPDATE mission_control_tool_adapters
            SET enabled = ?, updated_at = ?
            WHERE adapter_key = ?
            """,
            (1 if enabled else 0, now, adapter_key),
        )
        conn.commit()

    audit_log(
        actor=actor,
        action="tool_adapter_enabled_changed",
        target_type="tool_adapter",
        target_id=adapter_key,
        detail=f"Tool adapter enabled={enabled}.",
    )

    return get_tool_adapter(adapter_key) or {"status": "not_found", "adapter_key": adapter_key}


def _safe_project_path(relative_path: str | None = None) -> Path:
    root = Path(".").resolve()
    candidate = (root / (relative_path or ".")).resolve()

    if root not in candidate.parents and candidate != root:
        raise ValueError("Path escapes project boundary.")

    return candidate


def _run_local_file_adapter(action_name: str, payload: dict[str, Any]) -> dict[str, Any]:
    action = str(action_name or "").lower()

    if action == "list_project_files":
        base = _safe_project_path(payload.get("path") or ".")
        if not base.exists():
            return {"status": "not_found", "path": str(base)}
        if not base.is_dir():
            return {"status": "not_directory", "path": str(base)}

        files = []
        for item in sorted(base.iterdir(), key=lambda p: p.name.lower())[:200]:
            if item.name.startswith(".git"):
                continue
            files.append(
                {
                    "name": item.name,
                    "path": str(item.relative_to(Path(".").resolve())),
                    "is_dir": item.is_dir(),
                    "size_bytes": item.stat().st_size if item.is_file() else 0,
                }
            )

        return {
            "status": "ok",
            "action": action,
            "path": str(base),
            "files": files,
        }

    if action in {"read_project_file", "summarize_project_file"}:
        target = _safe_project_path(payload.get("path") or "")
        if not target.exists():
            return {"status": "not_found", "path": str(target)}
        if not target.is_file():
            return {"status": "not_file", "path": str(target)}

        max_bytes = int(payload.get("max_bytes") or 8000)
        raw = target.read_bytes()[:max(1, min(max_bytes, 50000))]
        text = raw.decode("utf-8", errors="replace")

        if action == "summarize_project_file":
            lines = text.splitlines()
            summary = {
                "line_count_sampled": len(lines),
                "char_count_sampled": len(text),
                "first_lines": lines[:10],
            }
            return {
                "status": "ok",
                "action": action,
                "path": str(target),
                "summary": summary,
            }

        return {
            "status": "ok",
            "action": action,
            "path": str(target),
            "content": text,
            "truncated": len(raw) >= max_bytes,
        }

    return {
        "status": "unsupported_action",
        "action": action,
        "supported_actions": [
            "list_project_files",
            "read_project_file",
            "summarize_project_file",
        ],
    }


def execute_tool_adapter_action(
    adapter_key: str,
    action_name: str,
    payload: dict[str, Any] | None = None,
    actor: str = "tool_adapter_runtime",
) -> dict[str, Any]:
    import json

    seed_default_tool_adapters()
    payload = payload or {}

    adapter = get_tool_adapter(adapter_key)
    if not adapter:
        return {"status": "not_found", "adapter_key": adapter_key}

    if int(adapter.get("enabled") or 0) != 1:
        return {"status": "disabled", "adapter_key": adapter_key}

    allowed_actions = {
        item.strip()
        for item in str(adapter.get("allowed_actions") or "").split(",")
        if item.strip()
    }

    if action_name not in allowed_actions:
        return {
            "status": "action_not_allowed",
            "adapter_key": adapter_key,
            "action_name": action_name,
            "allowed_actions": sorted(allowed_actions),
        }

    classification = classify_external_action(
        connector_key=adapter.get("connector_key") or "unknown",
        action_type=action_name,
        payload=payload,
    )

    firewall_action_id = None

    if classification.get("requires_approval"):
        firewall_action = create_external_action_request(
            {
                "connector_key": adapter.get("connector_key"),
                "action_type": action_name,
                "title": f"{adapter_key}:{action_name}",
                "requested_by": actor,
                "payload": payload,
            }
        )
        firewall_action_id = firewall_action.get("id")

        result = {
            "status": "pending_firewall_approval",
            "adapter_key": adapter_key,
            "action_name": action_name,
            "firewall_action_id": firewall_action_id,
            "classification": classification,
        }
    else:
        if adapter_key == "local_files":
            try:
                result = _run_local_file_adapter(action_name, payload)
            except ValueError as exc:
                result = {
                    "status": "blocked",
                    "adapter_key": adapter_key,
                    "action_name": action_name,
                    "reason": str(exc),
                }
        else:
            result = {
                "status": "adapter_placeholder",
                "adapter_key": adapter_key,
                "action_name": action_name,
                "message": "Adapter interface exists; real implementation not attached yet.",
            }

    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO mission_control_tool_adapter_runs
            (adapter_key, action_name, payload, status, result, firewall_action_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                adapter_key,
                action_name,
                json.dumps(payload),
                result.get("status") or "unknown",
                json.dumps(result),
                str(firewall_action_id or ""),
                now,
            ),
        )
        run_id = cursor.lastrowid
        conn.commit()

    audit_log(
        actor=actor,
        action="tool_adapter_action_executed",
        target_type="tool_adapter",
        target_id=adapter_key,
        detail=f"Adapter action {action_name} returned {result.get('status')}.",
    )

    result["run_id"] = run_id
    return result


def list_tool_adapter_runs(limit: int = 100) -> list[dict[str, Any]]:
    ensure_tool_adapter_tables()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        rows = conn.execute(
            "SELECT * FROM mission_control_tool_adapter_runs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_tool_adapter_state() -> dict[str, Any]:
    adapters = list_tool_adapters()
    runs = list_tool_adapter_runs(100)

    enabled = [adapter for adapter in adapters if int(adapter.get("enabled") or 0) == 1]
    ready = [adapter for adapter in adapters if str(adapter.get("status") or "").lower() == "ready"]

    return {
        "status": "ok",
        "counts": {
            "total": len(adapters),
            "enabled": len(enabled),
            "ready": len(ready),
            "runs": len(runs),
        },
        "adapters": adapters,
        "runs": runs,
        "recommended_action": (
            "Use the local file adapter to validate safe adapter execution."
            if enabled
            else "Enable a safe local adapter before execution."
        ),
    }


def ensure_model_provider_tables() -> None:
    with store.connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_model_providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_key TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                provider_type TEXT NOT NULL,
                status TEXT NOT NULL,
                enabled INTEGER NOT NULL,
                priority INTEGER NOT NULL,
                permission_level TEXT NOT NULL,
                config_summary TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_model_routes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_key TEXT NOT NULL UNIQUE,
                purpose TEXT NOT NULL,
                primary_provider TEXT NOT NULL,
                fallback_provider TEXT NOT NULL,
                policy TEXT NOT NULL,
                enabled INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_reasoning_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                route_key TEXT NOT NULL,
                prompt TEXT NOT NULL,
                context TEXT NOT NULL,
                status TEXT NOT NULL,
                provider_used TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.commit()


def seed_default_model_providers() -> None:
    ensure_model_provider_tables()
    now = datetime.now(timezone.utc).isoformat()

    providers = [
        {
            "provider_key": "local_placeholder",
            "name": "Local Placeholder Reasoner",
            "provider_type": "local_placeholder",
            "status": "ready",
            "enabled": 1,
            "priority": 1,
            "permission_level": "local_reasoning",
            "config_summary": "Safe local placeholder for model-routing tests. No external model call.",
        },
        {
            "provider_key": "openai_future",
            "name": "OpenAI Future Provider",
            "provider_type": "external_model",
            "status": "planned",
            "enabled": 0,
            "priority": 2,
            "permission_level": "external_model_runtime",
            "config_summary": "Planned external model provider. Requires model firewall and API key configuration.",
        },
        {
            "provider_key": "local_llm_future",
            "name": "Local LLM Future Provider",
            "provider_type": "local_model",
            "status": "planned",
            "enabled": 0,
            "priority": 3,
            "permission_level": "local_model_runtime",
            "config_summary": "Planned local model provider for offline/decentralized reasoning.",
        },
    ]

    routes = [
        {
            "route_key": "general_reasoning",
            "purpose": "General Salus reasoning and planning",
            "primary_provider": "local_placeholder",
            "fallback_provider": "local_placeholder",
            "policy": "Use safe local placeholder until real providers are configured.",
            "enabled": 1,
        },
        {
            "route_key": "daily_brief",
            "purpose": "Daily command brief generation",
            "primary_provider": "local_placeholder",
            "fallback_provider": "local_placeholder",
            "policy": "Local placeholder for brief synthesis.",
            "enabled": 1,
        },
        {
            "route_key": "risk_review",
            "purpose": "Risk classification and action review",
            "primary_provider": "local_placeholder",
            "fallback_provider": "local_placeholder",
            "policy": "Use conservative local placeholder for risk summaries.",
            "enabled": 1,
        },
    ]

    with store.connect() as conn:
        for provider in providers:
            conn.execute(
                """
                INSERT OR IGNORE INTO mission_control_model_providers
                (
                    provider_key, name, provider_type, status, enabled,
                    priority, permission_level, config_summary, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    provider["provider_key"],
                    provider["name"],
                    provider["provider_type"],
                    provider["status"],
                    provider["enabled"],
                    provider["priority"],
                    provider["permission_level"],
                    provider["config_summary"],
                    now,
                    now,
                ),
            )

        for route in routes:
            conn.execute(
                """
                INSERT OR IGNORE INTO mission_control_model_routes
                (
                    route_key, purpose, primary_provider, fallback_provider,
                    policy, enabled, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    route["route_key"],
                    route["purpose"],
                    route["primary_provider"],
                    route["fallback_provider"],
                    route["policy"],
                    route["enabled"],
                    now,
                    now,
                ),
            )

        conn.commit()


def list_model_providers(limit: int = 100) -> list[dict[str, Any]]:
    seed_default_model_providers()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        rows = conn.execute(
            "SELECT * FROM mission_control_model_providers ORDER BY priority ASC, id ASC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_model_provider(provider_key: str) -> dict[str, Any] | None:
    seed_default_model_providers()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        row = conn.execute(
            "SELECT * FROM mission_control_model_providers WHERE provider_key = ?",
            (provider_key,),
        ).fetchone()

    return dict(row) if row else None


def list_model_routes(limit: int = 100) -> list[dict[str, Any]]:
    seed_default_model_providers()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        rows = conn.execute(
            "SELECT * FROM mission_control_model_routes ORDER BY id ASC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_model_route(route_key: str) -> dict[str, Any] | None:
    seed_default_model_providers()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        row = conn.execute(
            "SELECT * FROM mission_control_model_routes WHERE route_key = ?",
            (route_key,),
        ).fetchone()

    return dict(row) if row else None


def upsert_model_provider_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    ensure_model_provider_tables()

    provider_key = str(payload.get("provider_key") or "").strip().lower().replace(" ", "_")
    if not provider_key:
        return {"status": "failed", "reason": "provider_key_required"}

    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        conn.execute(
            """
            INSERT INTO mission_control_model_providers
            (
                provider_key, name, provider_type, status, enabled, priority,
                permission_level, config_summary, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(provider_key) DO UPDATE SET
                name = excluded.name,
                provider_type = excluded.provider_type,
                status = excluded.status,
                enabled = excluded.enabled,
                priority = excluded.priority,
                permission_level = excluded.permission_level,
                config_summary = excluded.config_summary,
                updated_at = excluded.updated_at
            """,
            (
                provider_key,
                payload.get("name") or provider_key,
                payload.get("provider_type") or "generic_model",
                payload.get("status") or "planned",
                1 if payload.get("enabled") in {True, 1, "1", "true", "yes", "on"} else 0,
                int(payload.get("priority") or 10),
                payload.get("permission_level") or "external_model_runtime",
                payload.get("config_summary") or "",
                now,
                now,
            ),
        )
        conn.commit()

    audit_log(
        actor=payload.get("actor") or "commander",
        action="model_provider_upserted",
        target_type="model_provider",
        target_id=provider_key,
        detail=f"Model provider {provider_key} saved.",
    )

    return get_model_provider(provider_key) or {"status": "failed", "reason": "provider_not_found_after_upsert"}


def upsert_model_route_from_payload(payload: dict[str, Any]) -> dict[str, Any]:
    ensure_model_provider_tables()

    route_key = str(payload.get("route_key") or "").strip().lower().replace(" ", "_")
    if not route_key:
        return {"status": "failed", "reason": "route_key_required"}

    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        conn.execute(
            """
            INSERT INTO mission_control_model_routes
            (
                route_key, purpose, primary_provider, fallback_provider,
                policy, enabled, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(route_key) DO UPDATE SET
                purpose = excluded.purpose,
                primary_provider = excluded.primary_provider,
                fallback_provider = excluded.fallback_provider,
                policy = excluded.policy,
                enabled = excluded.enabled,
                updated_at = excluded.updated_at
            """,
            (
                route_key,
                payload.get("purpose") or "General reasoning route",
                payload.get("primary_provider") or "local_placeholder",
                payload.get("fallback_provider") or "local_placeholder",
                payload.get("policy") or "Use local placeholder until configured.",
                1 if payload.get("enabled") in {True, 1, "1", "true", "yes", "on"} else 0,
                now,
                now,
            ),
        )
        conn.commit()

    audit_log(
        actor=payload.get("actor") or "commander",
        action="model_route_upserted",
        target_type="model_route",
        target_id=route_key,
        detail=f"Model route {route_key} saved.",
    )

    return get_model_route(route_key) or {"status": "failed", "reason": "route_not_found_after_upsert"}


def _select_model_provider_for_route(route_key: str) -> dict[str, Any]:
    seed_default_model_providers()

    route = get_model_route(route_key) or get_model_route("general_reasoning")
    if not route:
        return {
            "status": "failed",
            "reason": "no_model_route_available",
            "provider_key": "none",
        }

    for provider_key in [route.get("primary_provider"), route.get("fallback_provider"), "local_placeholder"]:
        provider = get_model_provider(str(provider_key or ""))
        if provider and int(provider.get("enabled") or 0) == 1 and str(provider.get("status") or "").lower() in {"ready", "local_ready"}:
            provider["route_key"] = route.get("route_key")
            return provider

    return {
        "status": "failed",
        "reason": "no_enabled_provider_available",
        "provider_key": "none",
        "route_key": route.get("route_key"),
    }


def _run_local_placeholder_reasoner(prompt: str, context: str = "", route_key: str = "general_reasoning") -> dict[str, Any]:
    prompt_text = str(prompt or "").strip()
    context_text = str(context or "").strip()

    word_count = len(prompt_text.split())
    context_word_count = len(context_text.split())

    if not prompt_text:
        recommendation = "No prompt supplied. Provide a clear commander question or task."
    elif "risk" in prompt_text.lower() or "approve" in prompt_text.lower():
        recommendation = "Review risk, classify the action, require approval for external or sensitive changes, then execute only after audit logging."
    elif "mission" in prompt_text.lower():
        recommendation = "Convert the request into an active mission with priority, next action, owner, and AAR requirement."
    elif "brief" in prompt_text.lower():
        recommendation = "Generate a concise commander brief using current missions, risks, blockers, and next recommended action."
    else:
        recommendation = "Break the request into mission intent, current state, options, risks, and next action."

    return {
        "status": "ok",
        "provider": "local_placeholder",
        "route_key": route_key,
        "summary": f"Local placeholder processed {word_count} prompt words and {context_word_count} context words.",
        "recommendation": recommendation,
        "note": "No external model was called. This is a safe local placeholder response.",
    }


def create_reasoning_request(payload: dict[str, Any]) -> dict[str, Any]:
    import json

    ensure_model_provider_tables()

    route_key = payload.get("route_key") or "general_reasoning"
    prompt = payload.get("prompt") or ""
    context = payload.get("context") or ""

    provider = _select_model_provider_for_route(route_key)

    if provider.get("status") == "failed":
        result = {
            "status": "failed",
            "reason": provider.get("reason"),
        }
        provider_used = provider.get("provider_key") or "none"
        status = "failed"
    elif provider.get("provider_key") == "local_placeholder":
        result = _run_local_placeholder_reasoner(prompt, context, route_key=route_key)
        provider_used = "local_placeholder"
        status = "completed"
    else:
        firewall = create_external_action_request(
            {
                "connector_key": "model_providers",
                "action_type": "external_model_runtime",
                "title": f"Model reasoning request: {route_key}",
                "requested_by": payload.get("requested_by") or "model_router",
                "payload": {
                    "route_key": route_key,
                    "provider_key": provider.get("provider_key"),
                    "prompt_preview": str(prompt)[:500],
                },
            }
        )

        result = {
            "status": "pending_firewall_approval",
            "provider": provider.get("provider_key"),
            "firewall_action_id": firewall.get("id"),
            "note": "External model execution requires approval.",
        }
        provider_used = provider.get("provider_key")
        status = "pending_firewall_approval"

    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO mission_control_reasoning_requests
            (route_key, prompt, context, status, provider_used, result, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                route_key,
                prompt,
                context,
                status,
                provider_used,
                json.dumps(result),
                now,
            ),
        )
        request_id = cursor.lastrowid
        conn.commit()

    audit_log(
        actor=payload.get("requested_by") or "model_router",
        action="reasoning_request_created",
        target_type="reasoning_request",
        target_id=str(request_id),
        detail=f"Reasoning request routed to {provider_used} with status={status}.",
    )

    response = get_reasoning_request(request_id) or {"id": request_id, "status": status}
    response["parsed_result"] = result
    return response


def get_reasoning_request(request_id: int) -> dict[str, Any] | None:
    ensure_model_provider_tables()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        row = conn.execute(
            "SELECT * FROM mission_control_reasoning_requests WHERE id = ?",
            (request_id,),
        ).fetchone()

    return dict(row) if row else None


def list_reasoning_requests(limit: int = 100) -> list[dict[str, Any]]:
    ensure_model_provider_tables()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        rows = conn.execute(
            "SELECT * FROM mission_control_reasoning_requests ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_model_provider_state() -> dict[str, Any]:
    providers = list_model_providers()
    routes = list_model_routes()
    requests = list_reasoning_requests(100)

    enabled = [provider for provider in providers if int(provider.get("enabled") or 0) == 1]
    ready = [provider for provider in providers if str(provider.get("status") or "").lower() in {"ready", "local_ready"}]
    completed = [request for request in requests if str(request.get("status") or "").lower() == "completed"]
    pending = [request for request in requests if str(request.get("status") or "").lower() == "pending_firewall_approval"]

    return {
        "status": "ok",
        "counts": {
            "providers": len(providers),
            "enabled": len(enabled),
            "ready": len(ready),
            "routes": len(routes),
            "requests": len(requests),
            "completed": len(completed),
            "pending_firewall": len(pending),
        },
        "providers": providers,
        "routes": routes,
        "requests": requests,
        "recommended_action": "Keep local placeholder active until external model providers are configured and protected by firewall.",
    }


# -------------------------------------------------------------------
# Background Job Scheduler / Automation Loop
# -------------------------------------------------------------------

def ensure_background_job_tables() -> None:
    with store.connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_background_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_key TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                job_type TEXT NOT NULL,
                status TEXT NOT NULL,
                enabled INTEGER NOT NULL,
                schedule_hint TEXT NOT NULL,
                last_run_at TEXT,
                next_action TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_background_job_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_key TEXT NOT NULL,
                status TEXT NOT NULL,
                result TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )

        conn.commit()


def seed_default_background_jobs() -> None:
    ensure_background_job_tables()
    now = datetime.now(timezone.utc).isoformat()

    jobs = [
        {
            "job_key": "morning_command_loop",
            "name": "Morning Command Loop",
            "job_type": "daily_loop",
            "status": "ready",
            "enabled": 1,
            "schedule_hint": "manual_or_daily_morning",
            "next_action": "Generate morning daily loop, readiness review, and commander action.",
        },
        {
            "job_key": "evening_aar_loop",
            "name": "Evening AAR Loop",
            "job_type": "daily_loop",
            "status": "ready",
            "enabled": 1,
            "schedule_hint": "manual_or_daily_evening",
            "next_action": "Generate evening review and capture lessons.",
        },
        {
            "job_key": "snapshot_checkpoint",
            "name": "Snapshot Checkpoint",
            "job_type": "snapshot",
            "status": "ready",
            "enabled": 1,
            "schedule_hint": "before_major_build",
            "next_action": "Create a system snapshot before risky build changes.",
        },
        {
            "job_key": "agent_runtime_sweep",
            "name": "Agent Runtime Sweep",
            "job_type": "agent_runtime",
            "status": "ready",
            "enabled": 1,
            "schedule_hint": "manual_when_queue_has_items",
            "next_action": "Run next safe queued agent task.",
        },
        {
            "job_key": "health_contract_check",
            "name": "Health Contract Check",
            "job_type": "health_check",
            "status": "ready",
            "enabled": 1,
            "schedule_hint": "after_each_build",
            "next_action": "Check system health, route contract, and MVP readiness.",
        },
    ]

    with store.connect() as conn:
        for job in jobs:
            conn.execute(
                """
                INSERT OR IGNORE INTO mission_control_background_jobs
                (
                    job_key, name, job_type, status, enabled,
                    schedule_hint, last_run_at, next_action, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job["job_key"],
                    job["name"],
                    job["job_type"],
                    job["status"],
                    job["enabled"],
                    job["schedule_hint"],
                    None,
                    job["next_action"],
                    now,
                    now,
                ),
            )

        conn.commit()


def list_background_jobs(limit: int = 100) -> list[dict[str, Any]]:
    seed_default_background_jobs()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        rows = conn.execute(
            "SELECT * FROM mission_control_background_jobs ORDER BY id ASC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def get_background_job(job_key: str) -> dict[str, Any] | None:
    seed_default_background_jobs()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        row = conn.execute(
            "SELECT * FROM mission_control_background_jobs WHERE job_key = ?",
            (job_key,),
        ).fetchone()

    return dict(row) if row else None


def set_background_job_enabled(job_key: str, enabled: bool, actor: str = "commander") -> dict[str, Any]:
    ensure_background_job_tables()
    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        row = conn.execute(
            "SELECT id FROM mission_control_background_jobs WHERE job_key = ?",
            (job_key,),
        ).fetchone()

        if row is None:
            seed_default_background_jobs()
            row = conn.execute(
                "SELECT id FROM mission_control_background_jobs WHERE job_key = ?",
                (job_key,),
            ).fetchone()

        if row is None:
            return {"status": "not_found", "job_key": job_key}

        conn.execute(
            """
            UPDATE mission_control_background_jobs
            SET enabled = ?, updated_at = ?
            WHERE job_key = ?
            """,
            (1 if enabled else 0, now, job_key),
        )
        conn.commit()

    audit_log(
        actor=actor,
        action="background_job_enabled_changed",
        target_type="background_job",
        target_id=job_key,
        detail=f"Background job enabled={enabled}.",
    )

    return get_background_job(job_key) or {"status": "not_found", "job_key": job_key}


def record_background_job_run(job_key: str, status: str, result: dict[str, Any]) -> dict[str, Any]:
    import json

    ensure_background_job_tables()
    now = datetime.now(timezone.utc).isoformat()

    with store.connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO mission_control_background_job_runs
            (job_key, status, result, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                job_key,
                status,
                json.dumps(result),
                now,
            ),
        )
        run_id = cursor.lastrowid

        conn.execute(
            """
            UPDATE mission_control_background_jobs
            SET last_run_at = ?, status = ?, updated_at = ?
            WHERE job_key = ?
            """,
            (now, status, now, job_key),
        )

        conn.commit()

    return {
        "id": run_id,
        "job_key": job_key,
        "status": status,
        "result": result,
        "created_at": now,
    }


def list_background_job_runs(limit: int = 100) -> list[dict[str, Any]]:
    ensure_background_job_tables()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        rows = conn.execute(
            "SELECT * FROM mission_control_background_job_runs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]


def run_background_job(job_key: str, actor: str = "background_job_runner") -> dict[str, Any]:
    seed_default_background_jobs()
    job = get_background_job(job_key)

    if not job:
        return {"status": "not_found", "job_key": job_key}

    if int(job.get("enabled") or 0) != 1:
        result = {
            "status": "disabled",
            "job_key": job_key,
            "message": "Job is disabled.",
        }
        record_background_job_run(job_key, "disabled", result)
        return result

    job_type = str(job.get("job_type") or "").lower()

    if job_type == "daily_loop":
        loop_type = "morning" if "morning" in job_key else "evening" if "evening" in job_key else "full_cycle"
        result = create_daily_loop(loop_type=loop_type, actor=actor)
        status = "completed"

    elif job_type == "snapshot":
        result = create_system_snapshot(label=f"job_{job_key}", actor=actor)
        status = "completed" if result.get("status") == "created" else "failed"

    elif job_type == "agent_runtime":
        result = run_next_agent_task(actor=actor)
        status = "completed" if result.get("status") in {"completed", "idle"} else result.get("status", "unknown")

    elif job_type == "health_check":
        result = get_local_mvp_readiness()
        status = "completed" if result.get("status") in {"ready", "degraded"} else "failed"

    else:
        result = {
            "status": "unsupported_job_type",
            "job_key": job_key,
            "job_type": job_type,
        }
        status = "failed"

    run = record_background_job_run(job_key, status, result)

    audit_log(
        actor=actor,
        action="background_job_run",
        target_type="background_job",
        target_id=job_key,
        detail=f"Background job {job_key} completed with status={status}.",
    )

    return {
        "status": status,
        "job_key": job_key,
        "run": run,
        "result": result,
    }


def run_background_job_sweep(actor: str = "background_job_runner") -> dict[str, Any]:
    jobs = list_background_jobs()
    results = []

    for job in jobs:
        if int(job.get("enabled") or 0) != 1:
            continue

        job_key = str(job.get("job_key"))
        if job_key in {"health_contract_check"}:
            results.append(run_background_job(job_key, actor=actor))

    return {
        "status": "completed",
        "mode": "safe_sweep",
        "attempted": len(results),
        "results": results,
        "note": "Safe sweep only runs health-style jobs. Other jobs require manual trigger.",
    }


def get_background_job_state() -> dict[str, Any]:
    jobs = list_background_jobs()
    runs = list_background_job_runs(100)

    enabled = [job for job in jobs if int(job.get("enabled") or 0) == 1]
    ready = [job for job in jobs if str(job.get("status") or "").lower() in {"ready", "completed"}]
    failed = [job for job in jobs if str(job.get("status") or "").lower() == "failed"]

    return {
        "status": "ok",
        "counts": {
            "jobs": len(jobs),
            "enabled": len(enabled),
            "ready": len(ready),
            "failed": len(failed),
            "runs": len(runs),
        },
        "jobs": jobs,
        "runs": runs,
        "recommended_action": (
            "Run health contract check after each build. Run snapshots before risky changes."
            if jobs
            else "Seed background jobs."
        ),
    }


# -------------------------------------------------------------------
# Local Dashboard Authentication / Access Gate
# -------------------------------------------------------------------

def get_local_auth_config() -> dict[str, Any]:
    import os

    enabled_raw = os.getenv("SALUS_AUTH_ENABLED", "true").lower().strip()
    password = os.getenv("SALUS_LOCAL_PASSWORD", "salus-local")
    token = os.getenv("SALUS_LOCAL_TOKEN", "salus-local-token")

    enabled = enabled_raw not in {"0", "false", "no", "off"}

    return {
        "status": "ok",
        "enabled": enabled,
        "password_set": bool(password),
        "token_set": bool(token),
        "cookie_name": "salus_access",
        "login_path": "/mission-control/login",
        "default_password_warning": password == "salus-local",
        "recommended_action": (
            "Set SALUS_LOCAL_PASSWORD before exposing this outside localhost."
            if password == "salus-local"
            else "Local dashboard access gate configured."
        ),
    }


def verify_local_auth_password(password: str) -> bool:
    import os
    import hmac

    expected = os.getenv("SALUS_LOCAL_PASSWORD", "salus-local")
    return hmac.compare_digest(str(password or ""), expected)


def verify_local_auth_token(token: str | None) -> bool:
    import os
    import hmac

    config = get_local_auth_config()
    if not config.get("enabled"):
        return True

    expected = os.getenv("SALUS_LOCAL_TOKEN", "salus-local-token")
    return hmac.compare_digest(str(token or ""), expected)


def local_auth_cookie_value() -> str:
    import os

    return os.getenv("SALUS_LOCAL_TOKEN", "salus-local-token")


def get_local_auth_state() -> dict[str, Any]:
    config = get_local_auth_config()

    return {
        "status": "ok",
        "auth_enabled": config["enabled"],
        "password_set": config["password_set"],
        "token_set": config["token_set"],
        "default_password_warning": config["default_password_warning"],
        "recommended_action": config["recommended_action"],
    }


# -------------------------------------------------------------------
# Command Center Overview / Architecture Contract Repair
# -------------------------------------------------------------------

def get_command_center_overview() -> dict[str, Any]:
    readiness = get_local_mvp_readiness()

    return {
        "status": "ok",
        "readiness": readiness.get("status", "unknown"),
        "counts": {
            "active_missions": len(get_mission_control_state().get("active_missions", [])),
            "agent_tasks": get_agent_execution_state().get("counts", {}).get("total", 0),
            "runtime_queued": get_agent_runtime_state().get("counts", {}).get("queued", 0),
            "connectors": get_connector_registry_state().get("counts", {}).get("total", 0),
            "firewall_pending": get_external_action_firewall_state().get("counts", {}).get("pending_approval", 0),
            "tool_adapters": get_tool_adapter_state().get("counts", {}).get("total", 0),
            "model_requests": get_model_provider_state().get("counts", {}).get("requests", 0),
            "background_jobs": get_background_job_state().get("counts", {}).get("jobs", 0),
            "snapshots": get_snapshot_system_state().get("snapshot_count", 0),
        },
        "warnings": [
            "Default local password is active."
        ] if get_local_auth_state().get("default_password_warning") else [],
        "recommended_action": "Command Center operational. Continue controlled Phase 2 buildout.",
    }


def get_project_salus_architecture_manifest(app: Any | None = None) -> dict[str, Any]:
    manifest = {
        "status": "ok",
        "project": "Project Salus",
        "phase": "Local Phase 2 Foundation",
        "architecture_version": "2.0-local-foundation",
        "major_subsystems": [
            {"key": "mission_control", "name": "Mission Control Core"},
            {"key": "agent_execution", "name": "Agent Execution Registry"},
            {"key": "agent_runtime", "name": "Agent Runtime Worker"},
            {"key": "external_action_firewall", "name": "External Action Firewall"},
            {"key": "connectors", "name": "Connector Registry"},
            {"key": "tool_adapters", "name": "Tool Adapter Interface"},
            {"key": "model_providers", "name": "Model Provider Router"},
            {"key": "background_jobs", "name": "Background Job Scheduler"},
            {"key": "snapshots", "name": "Snapshot Backup System"},
            {"key": "records", "name": "Memory / Records Link-In"},
            {"key": "auth", "name": "Local Dashboard Access Gate"},
        ],
        "safety_controls": [
            "Local dashboard auth gate",
            "External action firewall",
            "Agent approval workflow",
            "Audit logs",
            "Snapshot backups",
        ],
    }

    if app is not None:
        routes = get_route_inventory(app)
        manifest["route_count"] = len(routes)
        manifest["mission_control_route_count"] = len(
            [route for route in routes if route.get("is_mission_control")]
        )

    return manifest


def get_project_salus_contract(app: Any | None = None) -> dict[str, Any]:
    required_routes = [
        "/mission-control/v1",
        "/mission-control/login",
        "/api/mission-control/dashboard",
        "/api/mission-control/mvp-readiness",
        "/api/mission-control/auth/status",
        "/api/mission-control/background-jobs",
        "/api/mission-control/model-providers",
        "/api/mission-control/tool-adapters",
        "/api/mission-control/firewall",
        "/api/mission-control/connectors",
        "/api/mission-control/agent-runtime",
        "/api/mission-control/agent/state",
        "/api/mission-control/snapshots",
        "/api/mission-control/export",
        "/api/mission-control/architecture",
        "/api/mission-control/system-contract",
    ]

    route_status = {"checked": False, "missing": [], "present": []}

    if app is not None:
        routes = get_route_inventory(app)
        paths = {route["path"] for route in routes}
        route_status = {
            "checked": True,
            "missing": [route for route in required_routes if route not in paths],
            "present": [route for route in required_routes if route in paths],
        }

    failures = []
    if route_status["checked"] and route_status["missing"]:
        failures.append("missing_required_routes")

    return {
        "status": "degraded" if failures else "ok",
        "contract_version": "2.0-local-foundation",
        "manifest": get_project_salus_architecture_manifest(app),
        "required_routes": required_routes,
        "route_status": route_status,
        "readiness": get_local_mvp_readiness(),
        "auth": get_local_auth_state(),
        "failures": failures,
        "recommended_action": (
            "Fix degraded contract checks before proceeding."
            if failures
            else "Project Salus Local Phase 2 contract is valid."
        ),
    }


# --------------------------------------------------------------------
# Production-Readiness / Security Hardening State
# -------------------------------------------------------------------

def get_security_hardening_state(app: Any | None = None) -> dict[str, Any]:
    import os

    auth_state = get_local_auth_state()
    readiness = get_local_mvp_readiness()

    env = os.getenv("SALUS_ENV", "local")
    auth_enabled = os.getenv("SALUS_AUTH_ENABLED", "true").lower().strip() not in {"0", "false", "no", "off"}
    default_password_active = auth_state.get("default_password_warning", False)

    external_actions_allowed = os.getenv("SALUS_ALLOW_EXTERNAL_ACTIONS", "false").lower().strip() in {"1", "true", "yes", "on"}
    model_external_calls_allowed = os.getenv("SALUS_ALLOW_MODEL_PROVIDER_EXTERNAL_CALLS", "false").lower().strip() in {"1", "true", "yes", "on"}
    connector_writes_allowed = os.getenv("SALUS_ALLOW_CONNECTOR_WRITES", "false").lower().strip() in {"1", "true", "yes", "on"}

    warnings = []
    blockers = []

    if not auth_enabled:
        blockers.append("Local dashboard authentication is disabled.")
    if default_password_active:
        warnings.append("Default local password is active. Set SALUS_LOCAL_PASSWORD.")
    if external_actions_allowed:
        warnings.append("External actions are enabled by environment flag.")
    if model_external_calls_allowed:
        warnings.append("External model-provider calls are enabled by environment flag.")
    if connector_writes_allowed:
        warnings.append("Connector writes are enabled by environment flag.")
    if readiness.get("status") not in {"ready", "ok"}:
        warnings.append("MVP readiness is degraded.")

    route_status = {"checked": False, "missing": [], "present": []}
    if app is not None:
        routes = get_route_inventory(app)
        paths = {route["path"] for route in routes}
        required_routes = [
            "/mission-control/login",
            "/mission-control/v1",
            "/api/mission-control/security",
            "/api/mission-control/auth/status",
            "/api/mission-control/firewall",
            "/api/mission-control/system-contract",
        ]
        route_status = {
            "checked": True,
            "missing": [route for route in required_routes if route not in paths],
            "present": [route for route in required_routes if route in paths],
        }
        if route_status["missing"]:
            blockers.append("Required security routes are missing.")

    status = "ok"
    if warnings:
        status = "warning"
    if blockers:
        status = "blocked"

    return {
        "status": status,
        "environment": env,
        "auth_enabled": auth_enabled,
        "default_password_active": default_password_active,
        "external_actions_allowed": external_actions_allowed,
        "model_external_calls_allowed": model_external_calls_allowed,
        "connector_writes_allowed": connector_writes_allowed,
        "required_security_headers": [
            "x-content-type-options",
            "x-frame-options",
            "referrer-policy",
            "permissions-policy",
            "cache-control",
        ],
        "warnings": warnings,
        "blockers": blockers,
        "route_status": route_status,
        "recommended_action": blockers[0] if blockers else warnings[0] if warnings else "Security hardening baseline is acceptable for local Phase 2.",
    }




# --------------------------------------------------------------------
# Phase 3: Local File Intelligence v2
# --------------------------------------------------------------------

def ensure_local_file_intelligence_tables() -> None:
    with store.connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mission_control_local_file_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                relative_path TEXT NOT NULL UNIQUE,
                file_name TEXT NOT NULL,
                file_extension TEXT NOT NULL,
                size_bytes INTEGER NOT NULL,
                line_count INTEGER NOT NULL,
                summary TEXT NOT NULL,
                indexed_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def _safe_project_root() -> Path:
    return Path(".").resolve()


def _is_indexable_local_file(path: Path) -> bool:
    ignored_parts = {
        ".git",
        ".venv",
        "__pycache__",
        ".pytest_cache",
        "snapshots",
        "node_modules",
        "dist",
        "build",
    }

    if any(part in ignored_parts for part in path.parts):
        return False

    if path.name.startswith(".") and path.name not in {".env.example", ".gitignore"}:
        return False

    if path.suffix.lower() not in {
        ".py",
        ".md",
        ".txt",
        ".json",
        ".yml",
        ".yaml",
        ".toml",
        ".sh",
        ".html",
        ".css",
        ".js",
    }:
        return False

    try:
        if path.stat().st_size > 250_000:
            return False
    except OSError:
        return False

    return True



def _summarize_local_file_text(text: str, max_chars: int = 500) -> str:
    clean = " ".join(text.replace("\n", " ").split())
    if not clean:
        return "Empty file."
    if len(clean) <= max_chars:
        return clean
    return clean[:max_chars].rstrip() + "..."



def reindex_local_file_intelligence(limit: int = 500, actor: str = "commander") -> dict[str, Any]:
    ensure_local_file_intelligence_tables()

    root = _safe_project_root()
    now = datetime.now(timezone.utc).isoformat()
    indexed = 0
    skipped = 0
    errors = []

    candidates = []
    for file_path in root.rglob("*"):
        if not file_path.is_file():
            continue
        try:
            relative_candidate = file_path.relative_to(root)
        except ValueError:
            skipped += 1
            continue

        if not _is_indexable_local_file(relative_candidate):
            skipped += 1
            continue

        candidates.append(file_path)

    candidates = candidates[:limit]

    with store.connect() as conn:
        for file_path in candidates:
            try:
                relative_path = str(file_path.relative_to(root))
                raw = file_path.read_text(errors="replace")
                summary = _summarize_local_file_text(raw)
                line_count = len(raw.splitlines())

                conn.execute(
                    """
                    INSERT INTO mission_control_local_file_index
                    (
                        relative_path, file_name, file_extension,
                        size_bytes, line_count, summary, indexed_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(relative_path) DO UPDATE SET
                        file_name = excluded.file_name,
                        file_extension = excluded.file_extension,
                        size_bytes = excluded.size_bytes,
                        line_count = excluded.line_count,
                        summary = excluded.summary,
                        indexed_at = excluded.indexed_at
                    """,
                    (
                        relative_path,
                        file_path.name,
                        file_path.suffix.lower(),
                        file_path.stat().st_size,
                        line_count,
                        summary,
                        now,
                    ),
                )
                indexed += 1
            except Exception as exc:
                errors.append({"path": str(file_path), "error": str(exc)})

        conn.commit()

    audit_log(
        actor=actor,
        action="local_file_intelligence_reindex",
        target_type="local_file_index",
        target_id="project_root",
        detail=f"Indexed {indexed} local files; skipped {skipped}; errors {len(errors)}.",
    )

    return {
        "status": "ok" if not errors else "partial",
        "indexed": indexed,
        "skipped": skipped,
        "errors": errors[:10],
        "indexed_at": now,
    }



def list_local_file_intelligence(limit: int = 100) -> list[dict[str, Any]]:
    ensure_local_file_intelligence_tables()

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        rows = conn.execute(
            """
            SELECT *
            FROM mission_control_local_file_index
            ORDER BY indexed_at DESC, relative_path ASC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]



def search_local_file_intelligence(query: str, limit: int = 50) -> list[dict[str, Any]]:
    ensure_local_file_intelligence_tables()

    q = f"%{query.strip()}%"
    if not query.strip():
        return list_local_file_intelligence(limit)

    with store.connect() as conn:
        conn.row_factory = __import__("sqlite3").Row
        rows = conn.execute(
            """
            SELECT *
            FROM mission_control_local_file_index
            WHERE relative_path LIKE ?
               OR file_name LIKE ?
               OR summary LIKE ?
               OR file_extension LIKE ?
            ORDER BY relative_path ASC
            LIMIT ?
            """,
            (q, q, q, q, limit),
        ).fetchall()

    return [dict(row) for row in rows]



def get_local_file_intelligence_state() -> dict[str, Any]:
    ensure_local_file_intelligence_tables()
    files = list_local_file_intelligence(100)

    extensions: dict[str, int] = {}
    total_size = 0

    for item in files:
        ext = item.get("file_extension") or "none"
        extensions[ext] = extensions.get(ext, 0) + 1
        total_size += int(item.get("size_bytes") or 0)

    return {
        "status": "ok",
        "counts": {
            "indexed_files": len(files),
            "extensions": extensions,
            "total_size_bytes_sample": total_size,
        },
        "files": files,
        "recommended_action": (
            "Run local file reindex after major code or document changes."
            if files
            else "Run local file intelligence reindex."
        ),
    }




# -----------------------------------------------------------------------------
# Phase 3: Connector Permission Profiles
# -----------------------------------------------------------------------------

CONNECTOR_PERMISSION_PROFILES = {
    "local_file_intelligence": {
        "connector_key": "local_file_intelligence",
        "display_name": "Local File Intelligence",
        "status": "enabled",
        "read_allowed": True,
        "write_allowed": False,
        "approval_required": False,
        "max_risk_level": "low",
        "notes": "Local read-only project file intelligence.",
    },
    "gmail_read_only": {
        "connector_key": "gmail_read_only",
        "display_name": "Gmail Read-Only",
        "status": "planned",
        "read_allowed": False,
        "write_allowed": False,
        "approval_required": True,
        "max_risk_level": "medium",
        "notes": "Planned connector. Disabled until explicitly enabled.",
    },
    "calendar_read_only": {
        "connector_key": "calendar_read_only",
        "display_name": "Calendar Read-Only",
        "status": "planned",
        "read_allowed": False,
        "write_allowed": False,
        "approval_required": True,
        "max_risk_level": "medium",
        "notes": "Planned connector. Disabled until explicitly enabled.",
    },
}


def _connector_risk_rank(value):
    return {"low": 1, "medium": 2, "high": 3, "critical": 4}.get(str(value or "").lower(), 4)


def list_connector_permission_profiles():
    return list(CONNECTOR_PERMISSION_PROFILES.values())


def get_connector_permission_profile(connector_key):
    return CONNECTOR_PERMISSION_PROFILES.get(connector_key)


def evaluate_connector_permission(connector_key, action_type, risk_level="low"):
    profile = get_connector_permission_profile(connector_key)
    action = str(action_type or "").lower().strip()
    risk = str(risk_level or "low").lower().strip()

    if not profile:
        return {
            "status": "blocked",
            "decision": "blocked",
            "connector_key": connector_key,
            "action_type": action,
            "risk_level": risk,
            "reason": "No connector permission profile exists.",
        }

    if profile.get("status") != "enabled":
        return {
            "status": "blocked",
            "decision": "blocked",
            "connector_key": connector_key,
            "action_type": action,
            "risk_level": risk,
            "profile": profile,
            "reason": f"Connector profile status is {profile.get('status')}.",
        }

    read_actions = {"read", "search", "list", "summarize", "inspect", "index"}
    write_actions = {"write", "send", "create", "update", "delete", "archive", "label", "move"}

    if action in read_actions and not profile.get("read_allowed"):
        decision = "blocked"
        reason = "Read actions are not allowed by this connector profile."
    elif action in write_actions and not profile.get("write_allowed"):
        decision = "blocked"
        reason = "Write actions are blocked by read-only connector policy."
    elif _connector_risk_rank(risk) > _connector_risk_rank(profile.get("max_risk_level")):
        decision = "pending_approval"
        reason = "Action risk exceeds profile max risk level."
    elif profile.get("approval_required") and risk in {"medium", "high", "critical"}:
        decision = "pending_approval"
        reason = "Approval required by connector permission profile."
    else:
        decision = "allowed"
        reason = "Action allowed by connector permission profile."

    return {
        "status": decision,
        "decision": decision,
        "connector_key": connector_key,
        "action_type": action,
        "risk_level": risk,
        "profile": profile,
        "reason": reason,
    }


def get_connector_permission_policy_state():
    profiles = list_connector_permission_profiles()
    read_only = [
        item for item in profiles
        if item.get("read_allowed") and not item.get("write_allowed")
    ]
    write_enabled = [
        item for item in profiles
        if item.get("write_allowed")
    ]

    return {
        "status": "ok" if not write_enabled else "warning",
        "counts": {
            "profiles": len(profiles),
            "read_only": len(read_only),
            "write_enabled": len(write_enabled),
        },
        "profiles": profiles,
        "recommended_action": (
            "Continue Phase 3 with read-only connector policy."
            if not write_enabled
            else "Investigate write-enabled connectors before proceeding."
        ),
    }



# -----------------------------------------------------------------------------
# Phase 3: Gmail Read-Only Connector Shell
# -----------------------------------------------------------------------------

GMAIL_READ_ONLY_CAPABILITIES = [
    {
        "capability": "list_recent_email_metadata",
        "status": "planned",
        "access_level": "read_only",
        "description": "List recent Gmail metadata after connector activation.",
    },
    {
        "capability": "search_email_metadata",
        "status": "planned",
        "access_level": "read_only",
        "description": "Search Gmail metadata after connector activation.",
    },
    {
        "capability": "summarize_email_thread",
        "status": "planned",
        "access_level": "read_only",
        "description": "Summarize selected email threads after connector activation.",
    },
]

GMAIL_READ_ONLY_BLOCKED_ACTIONS = [
    "send",
    "draft",
    "reply",
    "forward",
    "archive",
    "delete",
    "label",
    "move",
    "mark_read",
    "mark_unread",
]


def list_gmail_read_only_capabilities():
    return GMAIL_READ_ONLY_CAPABILITIES


def get_gmail_read_only_connector_state():
    permission = evaluate_connector_permission(
        "gmail_read_only",
        "read",
        "medium",
    )

    return {
        "status": "ok",
        "connector_key": "gmail_read_only",
        "display_name": "Gmail Read-Only Connector",
        "mode": "shell",
        "live_access_enabled": False,
        "read_only": True,
        "write_actions_blocked": True,
        "blocked_actions": GMAIL_READ_ONLY_BLOCKED_ACTIONS,
        "capabilities": list_gmail_read_only_capabilities(),
        "permission_check": permission,
        "recommended_action": (
            "Keep Gmail connector in shell mode until explicit read-only activation is approved."
        ),
    }


def evaluate_gmail_read_only_request(action_type, risk_level="medium"):
    action = str(action_type or "").lower().strip()

    if action in GMAIL_READ_ONLY_BLOCKED_ACTIONS:
        return {
            "status": "blocked",
            "decision": "blocked",
            "connector_key": "gmail_read_only",
            "action_type": action,
            "risk_level": risk_level,
            "reason": "Gmail write or mutation action blocked by read-only connector shell.",
        }

    return evaluate_connector_permission(
        "gmail_read_only",
        action,
        risk_level,
    )


def get_gmail_read_only_activation_plan():
    return {
        "status": "planned",
        "connector_key": "gmail_read_only",
        "activation_steps": [
            "Confirm connector permission profile remains read-only.",
            "Confirm no write, send, delete, archive, label, or draft operations are exposed.",
            "Add explicit commander approval gate before live Gmail access.",
            "Add audit logging for every Gmail read request.",
            "Add tests proving write actions remain blocked.",
        ],
        "required_controls": [
            "read_only_scope",
            "approval_gate",
            "audit_log",
            "permission_profile_check",
            "no_write_actions",
        ],
    }



# -----------------------------------------------------------------------------
# Phase 3: Calendar Read-Only Connector Shell
# -----------------------------------------------------------------------------

CALENDAR_READ_ONLY_CAPABILITIES = [
    {
        "capability": "list_calendar_events_metadata",
        "status": "planned",
        "access_level": "read_only",
        "description": "List calendar event metadata after connector activation.",
    },
    {
        "capability": "search_calendar_events",
        "status": "planned",
        "access_level": "read_only",
        "description": "Search calendar events after connector activation.",
    },
    {
        "capability": "summarize_daily_calendar",
        "status": "planned",
        "access_level": "read_only",
        "description": "Summarize daily schedule after connector activation.",
    },
]

CALENDAR_READ_ONLY_BLOCKED_ACTIONS = [
    "create",
    "update",
    "delete",
    "move",
    "invite",
    "respond",
    "accept",
    "decline",
    "tentative",
    "reschedule",
    "cancel",
]


def list_calendar_read_only_capabilities():
    return CALENDAR_READ_ONLY_CAPABILITIES


def get_calendar_read_only_connector_state():
    permission = evaluate_connector_permission(
        "calendar_read_only",
        "read",
        "medium",
    )

    return {
        "status": "ok",
        "connector_key": "calendar_read_only",
        "display_name": "Calendar Read-Only Connector",
        "mode": "shell",
        "live_access_enabled": False,
        "read_only": True,
        "write_actions_blocked": True,
        "blocked_actions": CALENDAR_READ_ONLY_BLOCKED_ACTIONS,
        "capabilities": list_calendar_read_only_capabilities(),
        "permission_check": permission,
        "recommended_action": (
            "Keep Calendar connector in shell mode until explicit read-only activation is approved."
        ),
    }


def evaluate_calendar_read_only_request(action_type, risk_level="medium"):
    action = str(action_type or "").lower().strip()

    if action in CALENDAR_READ_ONLY_BLOCKED_ACTIONS:
        return {
            "status": "blocked",
            "decision": "blocked",
            "connector_key": "calendar_read_only",
            "action_type": action,
            "risk_level": risk_level,
            "reason": "Calendar write or mutation action blocked by read-only connector shell.",
        }

    return evaluate_connector_permission(
        "calendar_read_only",
        action,
        risk_level,
    )


def get_calendar_read_only_activation_plan():
    return {
        "status": "planned",
        "connector_key": "calendar_read_only",
        "activation_steps": [
            "Confirm connector permission profile remains read-only.",
            "Confirm no create, update, delete, invite, respond, or reschedule operations are exposed.",
            "Add explicit commander approval gate before live Calendar access.",
            "Add audit logging for every Calendar read request.",
            "Add tests proving write actions remain blocked.",
        ],
        "required_controls": [
            "read_only_scope",
            "approval_gate",
            "audit_log",
            "permission_profile_check",
            "no_write_actions",
        ],
    }



# -----------------------------------------------------------------------------
# Phase 3: Unified Connector Readiness Registry
# -----------------------------------------------------------------------------

def _connector_readiness_entry(
    connector_key,
    display_name,
    mode,
    live_access_enabled,
    read_only,
    write_actions_blocked,
    permission_decision,
    readiness_status,
    recommended_action,
):
    return {
        "connector_key": connector_key,
        "display_name": display_name,
        "mode": mode,
        "live_access_enabled": live_access_enabled,
        "read_only": read_only,
        "write_actions_blocked": write_actions_blocked,
        "permission_decision": permission_decision,
        "readiness_status": readiness_status,
        "recommended_action": recommended_action,
    }


def list_connector_readiness_registry():
    local_permission = evaluate_connector_permission(
        "local_file_intelligence",
        "read",
        "low",
    )

    gmail_state = get_gmail_read_only_connector_state()
    calendar_state = get_calendar_read_only_connector_state()

    return [
        _connector_readiness_entry(
            connector_key="local_file_intelligence",
            display_name="Local File Intelligence",
            mode="active_backend",
            live_access_enabled=True,
            read_only=True,
            write_actions_blocked=True,
            permission_decision=local_permission.get("decision"),
            readiness_status="ready_read_only",
            recommended_action="Continue using as read-only local intelligence source.",
        ),
        _connector_readiness_entry(
            connector_key="gmail_read_only",
            display_name="Gmail Read-Only Connector",
            mode=gmail_state.get("mode"),
            live_access_enabled=gmail_state.get("live_access_enabled"),
            read_only=gmail_state.get("read_only"),
            write_actions_blocked=gmail_state.get("write_actions_blocked"),
            permission_decision=gmail_state.get("permission_check", {}).get("decision"),
            readiness_status="shell_only",
            recommended_action=gmail_state.get("recommended_action"),
        ),
        _connector_readiness_entry(
            connector_key="calendar_read_only",
            display_name="Calendar Read-Only Connector",
            mode=calendar_state.get("mode"),
            live_access_enabled=calendar_state.get("live_access_enabled"),
            read_only=calendar_state.get("read_only"),
            write_actions_blocked=calendar_state.get("write_actions_blocked"),
            permission_decision=calendar_state.get("permission_check", {}).get("decision"),
            readiness_status="shell_only",
            recommended_action=calendar_state.get("recommended_action"),
        ),
    ]


def get_connector_readiness(connector_key):
    for item in list_connector_readiness_registry():
        if item.get("connector_key") == connector_key:
            return item

    return {
        "status": "not_found",
        "connector_key": connector_key,
        "readiness_status": "unknown",
        "recommended_action": "Create connector permission profile before use.",
    }


def get_connector_readiness_registry_state():
    connectors = list_connector_readiness_registry()

    ready = [
        item for item in connectors
        if item.get("readiness_status") == "ready_read_only"
    ]
    shell_only = [
        item for item in connectors
        if item.get("readiness_status") == "shell_only"
    ]
    write_enabled = [
        item for item in connectors
        if item.get("write_actions_blocked") is False
    ]

    return {
        "status": "ok" if not write_enabled else "warning",
        "counts": {
            "connectors": len(connectors),
            "ready_read_only": len(ready),
            "shell_only": len(shell_only),
            "write_enabled": len(write_enabled),
        },
        "connectors": connectors,
        "recommended_action": (
            "Continue Phase 3 with read-only connector activation controls."
            if not write_enabled
            else "Investigate write-enabled connectors before proceeding."
        ),
    }



# -----------------------------------------------------------------------------
# Phase 3: Connector Activation Gate
# -----------------------------------------------------------------------------

CONNECTOR_ACTIVATION_REQUIRED_CONTROLS = {
    "read_only_scope",
    "approval_gate",
    "audit_log",
    "permission_profile_check",
    "no_write_actions",
}


def evaluate_connector_activation_gate(connector_key, requested_controls=None):
    requested_controls = set(requested_controls or [])
    readiness = get_connector_readiness(connector_key)
    profile = get_connector_permission_profile(connector_key)

    if readiness.get("status") == "not_found" or not profile:
        return {
            "status": "blocked",
            "decision": "blocked",
            "connector_key": connector_key,
            "reason": "Connector readiness or permission profile not found.",
            "missing_controls": sorted(CONNECTOR_ACTIVATION_REQUIRED_CONTROLS),
        }

    missing_controls = sorted(CONNECTOR_ACTIVATION_REQUIRED_CONTROLS - requested_controls)

    if profile.get("write_allowed") is True:
        return {
            "status": "blocked",
            "decision": "blocked",
            "connector_key": connector_key,
            "reason": "Write-enabled connectors cannot pass the Phase 3 read-only activation gate.",
            "readiness": readiness,
            "profile": profile,
            "missing_controls": missing_controls,
        }

    if missing_controls:
        return {
            "status": "pending_controls",
            "decision": "pending_controls",
            "connector_key": connector_key,
            "reason": "Required activation controls are missing.",
            "readiness": readiness,
            "profile": profile,
            "required_controls": sorted(CONNECTOR_ACTIVATION_REQUIRED_CONTROLS),
            "provided_controls": sorted(requested_controls),
            "missing_controls": missing_controls,
        }

    if profile.get("status") != "enabled":
        return {
            "status": "pending_approval",
            "decision": "pending_approval",
            "connector_key": connector_key,
            "reason": "Connector profile is not enabled; commander approval required before activation.",
            "readiness": readiness,
            "profile": profile,
            "required_controls": sorted(CONNECTOR_ACTIVATION_REQUIRED_CONTROLS),
            "provided_controls": sorted(requested_controls),
            "missing_controls": [],
        }

    return {
        "status": "ready_for_read_only_activation",
        "decision": "ready_for_read_only_activation",
        "connector_key": connector_key,
        "reason": "Connector satisfies Phase 3 read-only activation controls.",
        "readiness": readiness,
        "profile": profile,
        "required_controls": sorted(CONNECTOR_ACTIVATION_REQUIRED_CONTROLS),
        "provided_controls": sorted(requested_controls),
        "missing_controls": [],
    }


def create_connector_activation_request(connector_key, requested_controls=None, actor="commander"):
    gate = evaluate_connector_activation_gate(connector_key, requested_controls)
    request_id = f"connector_activation_{connector_key}"

    audit_log(
        actor=actor,
        action="connector_activation_gate_evaluated",
        target_type="connector_activation",
        target_id=request_id,
        detail=f"Connector activation gate evaluated for {connector_key}: {gate.get('decision')}.",
    )

    return {
        "status": "ok",
        "request_id": request_id,
        "connector_key": connector_key,
        "gate": gate,
        "requires_commander_approval": gate.get("decision") in {
            "pending_approval",
            "ready_for_read_only_activation",
        },
        "recommended_action": (
            "Review gate result and approve only if connector remains read-only."
        ),
    }


def get_connector_activation_gate_state():
    connectors = list_connector_readiness_registry()
    evaluations = [
        evaluate_connector_activation_gate(
            item.get("connector_key"),
            CONNECTOR_ACTIVATION_REQUIRED_CONTROLS,
        )
        for item in connectors
    ]

    ready = [
        item for item in evaluations
        if item.get("decision") == "ready_for_read_only_activation"
    ]
    pending = [
        item for item in evaluations
        if item.get("decision") in {"pending_approval", "pending_controls"}
    ]
    blocked = [
        item for item in evaluations
        if item.get("decision") == "blocked"
    ]

    return {
        "status": "ok" if not blocked else "warning",
        "counts": {
            "evaluated": len(evaluations),
            "ready_for_read_only_activation": len(ready),
            "pending": len(pending),
            "blocked": len(blocked),
        },
        "required_controls": sorted(CONNECTOR_ACTIVATION_REQUIRED_CONTROLS),
        "evaluations": evaluations,
        "recommended_action": "Keep shell connectors pending approval until live read-only integrations are explicitly authorized.",
    }



# -----------------------------------------------------------------------------
# Phase 3: Daily Driver Startup + Health Check
# -----------------------------------------------------------------------------

def _daily_driver_component(name, status, detail="", recommended_action=""):
    return {
        "name": name,
        "status": status,
        "detail": detail,
        "recommended_action": recommended_action,
    }


def get_daily_driver_health_state():
    components = []

    try:
        with store.connect() as conn:
            conn.execute("SELECT 1").fetchone()
        components.append(
            _daily_driver_component(
                "database",
                "ok",
                "SQLite store is reachable.",
                "Continue.",
            )
        )
    except Exception as exc:
        components.append(
            _daily_driver_component(
                "database",
                "fail",
                f"Database check failed: {exc}",
                "Repair local database/store before daily use.",
            )
        )

    components.append(
        _daily_driver_component(
            "mission_control",
            "ok",
            "Mission Control service layer is available.",
            "Open /mission-control/v1.",
        )
    )

    try:
        local_state = get_local_file_intelligence_state()
        indexed = local_state.get("counts", {}).get("indexed_files", 0)
        components.append(
            _daily_driver_component(
                "local_file_intelligence",
                "ok",
                f"Local file intelligence available. Indexed file sample: {indexed}.",
                "Run reindex after major code or document changes.",
            )
        )
    except Exception as exc:
        components.append(
            _daily_driver_component(
                "local_file_intelligence",
                "warning",
                f"Local file intelligence unavailable: {exc}",
                "Run local file intelligence repair or reindex.",
            )
        )

    try:
        policy = get_connector_permission_policy_state()
        write_enabled = policy.get("counts", {}).get("write_enabled", 0)
        components.append(
            _daily_driver_component(
                "connector_permission_policy",
                "ok" if write_enabled == 0 else "warning",
                f"Connector profiles loaded. Write-enabled connectors: {write_enabled}.",
                "Keep connectors read-only until explicitly approved.",
            )
        )
    except Exception as exc:
        components.append(
            _daily_driver_component(
                "connector_permission_policy",
                "warning",
                f"Connector permission policy unavailable: {exc}",
                "Complete connector permission profile block.",
            )
        )

    try:
        gmail = get_gmail_read_only_connector_state()
        components.append(
            _daily_driver_component(
                "gmail_read_only_shell",
                "ok",
                f"Gmail shell mode: {gmail.get('mode')}; live access: {gmail.get('live_access_enabled')}.",
                "Keep shell-only until explicit activation.",
            )
        )
    except Exception as exc:
        components.append(
            _daily_driver_component(
                "gmail_read_only_shell",
                "warning",
                f"Gmail shell unavailable: {exc}",
                "Complete Gmail read-only connector shell block.",
            )
        )

    try:
        calendar = get_calendar_read_only_connector_state()
        components.append(
            _daily_driver_component(
                "calendar_read_only_shell",
                "ok",
                f"Calendar shell mode: {calendar.get('mode')}; live access: {calendar.get('live_access_enabled')}.",
                "Keep shell-only until explicit activation.",
            )
        )
    except Exception as exc:
        components.append(
            _daily_driver_component(
                "calendar_read_only_shell",
                "warning",
                f"Calendar shell unavailable: {exc}",
                "Complete Calendar read-only connector shell block.",
            )
        )

    try:
        readiness = get_connector_readiness_registry_state()
        components.append(
            _daily_driver_component(
                "connector_readiness_registry",
                readiness.get("status", "ok"),
                f"Connector readiness count: {readiness.get('counts', {}).get('connectors', 0)}.",
                readiness.get("recommended_action", "Continue."),
            )
        )
    except Exception as exc:
        components.append(
            _daily_driver_component(
                "connector_readiness_registry",
                "warning",
                f"Connector readiness registry unavailable: {exc}",
                "Complete connector readiness registry block.",
            )
        )

    try:
        gate = get_connector_activation_gate_state()
        components.append(
            _daily_driver_component(
                "connector_activation_gate",
                gate.get("status", "ok"),
                f"Activation gate evaluated connectors: {gate.get('counts', {}).get('evaluated', 0)}.",
                gate.get("recommended_action", "Continue."),
            )
        )
    except Exception as exc:
        components.append(
            _daily_driver_component(
                "connector_activation_gate",
                "warning",
                f"Connector activation gate unavailable: {exc}",
                "Complete connector activation gate block.",
            )
        )

    fail_count = len([item for item in components if item.get("status") == "fail"])
    warning_count = len([item for item in components if item.get("status") == "warning"])
    ok_count = len([item for item in components if item.get("status") == "ok"])

    if fail_count:
        overall = "not_ready"
        recommended_action = "Fix failed components before using Project Salus as daily driver."
    elif warning_count:
        overall = "usable_with_warnings"
        recommended_action = "Usable for daily local operations. Avoid live connector activation until warnings are resolved."
    else:
        overall = "ready"
        recommended_action = "Project Salus is ready for daily local use. Start Daily Commander Brief."

    return {
        "status": overall,
        "daily_use_ready": fail_count == 0,
        "counts": {
            "ok": ok_count,
            "warnings": warning_count,
            "failures": fail_count,
            "components": len(components),
        },
        "components": components,
        "recommended_action": recommended_action,
        "next_daily_action": "Open Mission Control and run Start My Day workflow.",
    }
