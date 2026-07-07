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
