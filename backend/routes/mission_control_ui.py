from __future__ import annotations

import html
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from urllib.parse import parse_qs

from backend import mission_control_store as mc_store
from backend import mission_control_service as mc_service
from backend import mission_control_views as mc_views
from backend.routes.mission_control_auth import require_local_dashboard_auth



router = APIRouter(tags=["mission-control-ui"])


def _db_path() -> Path:
    return mc_store.db_path()


def _connect() -> sqlite3.Connection:
    return mc_store.connect()


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    return mc_store.table_exists(conn, table)


def _safe_rows(conn: sqlite3.Connection, table: str, limit: int = 10) -> list[dict[str, Any]]:
    return mc_store.safe_rows(conn, table, limit)




def _ensure_commander_briefs_table(conn: sqlite3.Connection) -> None:
    mc_store.ensure_tables(conn)


def _ensure_daily_workflow_table(conn: sqlite3.Connection) -> None:
    mc_store.ensure_tables(conn)


def _ensure_operator_queue_table(conn: sqlite3.Connection) -> None:
    mc_store.ensure_tables(conn)


def _value(row: dict[str, Any] | None, *keys: str, default: str = "") -> str:
    if not row:
        return default
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return default


def _cell(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value))


def _ensure_operator_queue_table(conn: sqlite3.Connection) -> None:
    mc_store.ensure_tables(conn)


def _ensure_daily_workflow_table(conn: sqlite3.Connection) -> None:
    mc_store.ensure_tables(conn)


def _daily_workflow_content(workflow_type: str, missions: list[dict[str, Any]], sitreps: list[dict[str, Any]], aars: list[dict[str, Any]]) -> str:
    open_missions = [
        mission for mission in missions
        if str(mission.get("status", "")).lower() not in {"complete", "completed", "done"}
    ]
    blocked_missions = [
        mission for mission in missions
        if str(mission.get("status", "")).lower() == "blocked"
    ]

    top_mission = open_missions[0] if open_missions else {}
    latest_sitrep = sitreps[0] if sitreps else {}
    latest_aar = aars[0] if aars else {}

    if workflow_type == "morning_brief":
        return "\n".join([
            "PROJECT SALUS MORNING BRIEF",
            "",
            f"Open Missions: {len(open_missions)}",
            f"Blocked Missions: {len(blocked_missions)}",
            "",
            "Priority Lock:",
            _value(top_mission, "title", default="Create today's priority mission."),
            "",
            "Next Action:",
            _value(top_mission, "next_action", default="Define the first executable action."),
            "",
            "Latest SITREP:",
            _value(latest_sitrep, "top_priority", default="No SITREP captured."),
            "",
            "Commander Intent:",
            "Execute the highest-value action before expanding scope.",
        ])

    return "\n".join([
        "PROJECT SALUS EVENING AAR",
        "",
        "Review Focus:",
        _value(top_mission, "title", default="No active mission selected."),
        "",
        "What changed today:",
        _value(latest_sitrep, "top_priority", default="No SITREP captured."),
        "",
        "Latest Lesson:",
        _value(latest_aar, "lesson_learned", "lesson", default="No AAR lesson captured."),
        "",
        "Tomorrow's First Move:",
        _value(top_mission, "next_action", default="Set tomorrow's first action."),
    ])



def _agent_panel_context() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    try:
        agent_state = mc_service.get_agent_execution_state()
        return (
            agent_state.get("tasks", []),
            agent_state.get("audit_log", []),
        )
    except Exception:
        return ([], [])


def _operator_queue_table(rows: list[dict[str, Any]]) -> str:
    return mc_views.render_operator_queue_table(rows)




def _build_commander_brief(
    missions: list[dict[str, Any]],
    sitreps: list[dict[str, Any]],
    aars: list[dict[str, Any]],
) -> str:
    return mc_service.build_commander_brief(missions, sitreps, aars)


def _mission_queue(rows: list[dict[str, Any]]) -> str:
    active = [
        row for row in rows
        if str(row.get("status", "")).lower() not in {"complete", "completed", "done"}
    ]

    if not active:
        return """
        <section class="card">
          <h2>Today Mission Queue</h2>
          <p class="muted">No active missions. Create one mission to drive execution.</p>
        </section>
        """

    items = ""
    for index, mission in enumerate(active[:5], start=1):
        items += f"""
        <div class="queue-item">
          <div class="queue-rank">#{index}</div>
          <div>
            <strong>{html.escape(str(mission.get("title", "Untitled Mission")))}</strong>
            <p>{html.escape(str(mission.get("next_action", "No next action set.")))}</p>
            <span>Status: {html.escape(str(mission.get("status", "")))} | Priority: {html.escape(str(mission.get("priority", "")))}</span>
          </div>
        </div>
        """

    return f"""
    <section class="card">
      <h2>Today Mission Queue</h2>
      <p class="muted">Execute in order. Do not expand scope until #1 moves.</p>
      {items}
    </section>
    """


def _table(title: str, rows: list[dict[str, Any]]) -> str:
    if not rows:
        return f"""
        <section class="card">
          <h2>{html.escape(title)}</h2>
          <p class="muted">No records yet.</p>
        </section>
        """

    columns = list(rows[0].keys())
    action_column = title.lower() == "missions" and "id" in columns
    headers = "".join(f"<th>{html.escape(col)}</th>" for col in columns)

    if action_column:
        headers += "<th>Actions</th>"

    body = ""
    for row in rows:
        body += "<tr>" + "".join(f"<td>{_cell(row.get(col))}</td>" for col in columns)

        if action_column:
            mission_id = html.escape(str(row.get("id")))
            body += f"""
            <td class="actions">
              <form method="post" action="/mission-control/mission/{mission_id}/status/active">
                <button type="submit">Active</button>
              </form>
              <form method="post" action="/mission-control/mission/{mission_id}/status/blocked">
                <button type="submit">Blocked</button>
              </form>
              <form method="post" action="/mission-control/mission/{mission_id}/status/complete">
                <button type="submit">Complete</button>
              </form>
            </td>
            """

        body += "</tr>"

    return f"""
    <section class="card">
      <h2>{html.escape(title)}</h2>
      <div class="table-wrap">
        <table>
          <thead><tr>{headers}</tr></thead>
          <tbody>{body}</tbody>
        </table>
      </div>
    </section>
    """


def _form_value(form: dict[str, list[str]], key: str, default: str = "") -> str:
    values = form.get(key)
    if not values:
        return default
    return values[0].strip()


def _insert_dynamic_with_conn(conn: sqlite3.Connection, table: str, values: dict[str, Any]) -> None:
    mc_store.insert_dynamic(conn, table, values)


def _insert_dynamic(table: str, values: dict[str, Any]) -> None:
    with _connect() as conn:
        mc_store.insert_dynamic(conn, table, values)
        conn.commit()


@router.post("/mission-control/mission")
async def create_mission_from_ui(request: Request):
    raw = (await request.body()).decode()
    form = parse_qs(raw)

    _insert_dynamic(
        "missions",
        {
            "title": _form_value(form, "title", "Untitled Mission"),
            "status": _form_value(form, "status", "active"),
            "priority": _form_value(form, "priority", "medium"),
            "next_action": _form_value(form, "next_action", ""),
        },
    )

    return RedirectResponse("/mission-control/ui", status_code=303)


@router.post("/mission-control/sitrep")
async def create_sitrep_from_ui(request: Request):
    raw = (await request.body()).decode()
    form = parse_qs(raw)

    _insert_dynamic(
        "sitreps",
        {
            "top_priority": _form_value(form, "top_priority", ""),
            "blocker": _form_value(form, "blocker", ""),
            "action_1": _form_value(form, "action_1", ""),
            "action_2": _form_value(form, "action_2", ""),
            "action_3": _form_value(form, "action_3", ""),
        },
    )

    return RedirectResponse("/mission-control/ui", status_code=303)


@router.post("/mission-control/aar")
async def create_aar_from_ui(request: Request):
    raw = (await request.body()).decode()
    form = parse_qs(raw)

    mission_value = _form_value(form, "mission_id", "Mission Control")

    _insert_dynamic(
        "aars",
        {
            "mission": mission_value or "Mission Control",
            "mission_id": mission_value,
            "what_happened": _form_value(form, "what_happened", ""),
            "what_worked": _form_value(form, "what_worked", ""),
            "what_failed": _form_value(form, "what_failed", ""),
            "lesson": _form_value(form, "lesson", ""),
            "next_action": _form_value(form, "next_action", ""),
        },
    )

    return RedirectResponse("/mission-control/ui", status_code=303)


@router.post("/mission-control/mission/{mission_id}/status/{status}")
def update_mission_status_from_ui(mission_id: int, status: str):
    allowed = {"active", "blocked", "complete"}
    if status not in allowed:
        return RedirectResponse("/mission-control/ui", status_code=303)

    with _connect() as conn:
        if _table_exists(conn, "missions"):
            columns = {
                row["name"]
                for row in conn.execute("PRAGMA table_info(missions)").fetchall()
            }

            if "status" in columns and "id" in columns:
                conn.execute(
                    "UPDATE missions SET status = ? WHERE id = ?",
                    (status, mission_id),
                )
                conn.commit()

    return RedirectResponse("/mission-control/ui", status_code=303)


@router.post("/mission-control/commander-brief")
def generate_commander_brief_from_ui():
    with _connect() as conn:
        _ensure_commander_briefs_table(conn)
        missions = _safe_rows(conn, "missions", 50)
        sitreps = _safe_rows(conn, "sitreps", 20)
        aars = _safe_rows(conn, "aars", 20)

        brief = _build_commander_brief(missions, sitreps, aars)
        now = datetime.now(timezone.utc).isoformat()

        conn.execute(
            "INSERT INTO mission_control_briefs (title, brief, created_at) VALUES (?, ?, ?)",
            ("Daily Commander Brief", brief, now),
        )
        conn.commit()

    return RedirectResponse("/mission-control/ui", status_code=303)


@router.post("/mission-control/daily-workflow/{workflow_type}")
def generate_daily_workflow_from_ui(workflow_type: str):
    allowed = {"morning_brief", "evening_aar"}
    if workflow_type not in allowed:
        return RedirectResponse("/mission-control/ui", status_code=303)

    with _connect() as conn:
        _ensure_daily_workflow_table(conn)
        missions = _safe_rows(conn, "missions", 50)
        sitreps = _safe_rows(conn, "sitreps", 20)
        aars = _safe_rows(conn, "aars", 20)
        now = datetime.now(timezone.utc).isoformat()

        title = "Morning Brief" if workflow_type == "morning_brief" else "Evening AAR"
        content = _daily_workflow_content(workflow_type, missions, sitreps, aars)

        conn.execute(
            "INSERT INTO mission_control_daily_workflow (workflow_type, title, content, created_at) VALUES (?, ?, ?, ?)",
            (workflow_type, title, content, now),
        )
        conn.commit()

    return RedirectResponse("/mission-control/ui", status_code=303)


@router.get("/mission-control/brief/latest", response_class=HTMLResponse)
def latest_brief_print_view() -> str:
    with _connect() as conn:
        _ensure_commander_briefs_table(conn)
        _ensure_daily_workflow_table(conn)

        commander = _safe_rows(conn, "mission_control_briefs", 1)
        workflows = _safe_rows(conn, "mission_control_daily_workflow", 1)

    latest = commander[0] if commander else None
    if workflows and (not latest or str(workflows[0].get("created_at", "")) > str(latest.get("created_at", ""))):
        latest = workflows[0]

    title = _value(latest, "title", default="No Brief Available") if latest else "No Brief Available"
    content = _value(latest, "brief", "content", default="Generate a brief first.") if latest else "Generate a brief first."

    return f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>{html.escape(title)}</title>
      <style>
        body {{
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          max-width: 900px;
          margin: 40px auto;
          padding: 20px;
          line-height: 1.5;
          color: #111;
          background: #fff;
        }}
        pre {{
          white-space: pre-wrap;
          font-size: 15px;
        }}
        .actions {{
          margin-bottom: 20px;
        }}
        button, a {{
          display: inline-block;
          margin-right: 8px;
          padding: 10px 14px;
          border: 1px solid #222;
          border-radius: 8px;
          color: #111;
          background: #f4f4f4;
          text-decoration: none;
          cursor: pointer;
        }}
        @media print {{
          .actions {{ display: none; }}
          body {{ margin: 0; }}
        }}
      </style>
    </head>
    <body>
      <div class="actions">
        <button onclick="window.print()">Print / Save PDF</button>
        <a href="/mission-control/ui">Back to Mission Control</a>
      </div>
      <h1>{html.escape(title)}</h1>
      <pre>{html.escape(content)}</pre>

      <script>
        async function refreshLiveStatus() {{
          try {{
            const response = await fetch("/api/mission-control/live-status");
            const data = await response.json();

            document.getElementById("active-count").textContent = data.active_missions;
            document.getElementById("blocked-count").textContent = data.blocked_missions;

            const latest = data.latest_mission && data.latest_mission.title
              ? data.latest_mission.title
              : "No active mission";

            document.getElementById("live-status").textContent =
              "Live: " + data.status.toUpperCase() +
              " | Active: " + data.active_missions +
              " | Blocked: " + data.blocked_missions +
              " | Focus: " + latest +
              " | Updated: " + new Date().toLocaleTimeString();
          }} catch (error) {{
            document.getElementById("live-status").textContent = "Live status unavailable.";
          }}
        }}

        refreshLiveStatus();
        setInterval(refreshLiveStatus, 15000);
      </script>

    </body>
    </html>
    """


@router.get("/mission-control")
def mission_control_default(request: Request):
    auth_redirect = require_local_dashboard_auth(request)
    if auth_redirect:
        return auth_redirect

    return RedirectResponse("/mission-control/v1", status_code=307)

@router.get("/mission-control/ui", response_class=HTMLResponse)
def mission_control_ui(request: Request) -> str:
    auth_redirect = require_local_dashboard_auth(request)
    if auth_redirect:
        return auth_redirect


    with _connect() as conn:
        _ensure_commander_briefs_table(conn)
        missions = _safe_rows(conn, "missions", 10)
        sitreps = _safe_rows(conn, "sitreps", 10)
        aars = _safe_rows(conn, "aars", 10)
        agents = _safe_rows(conn, "agents", 10)
        commander_briefs = _safe_rows(conn, "mission_control_briefs", 5)
        _ensure_daily_workflow_table(conn)
        daily_workflows = _safe_rows(conn, "mission_control_daily_workflow", 5)

    active_missions = [
        mission for mission in missions
        if str(mission.get("status", "")).lower() not in {"complete", "completed", "done"}
    ]

    top_priority = "No active mission loaded."
    if active_missions:
        top_priority = str(
            active_missions[0].get("next_action")
            or active_missions[0].get("title")
            or "Review active mission."
        )

    agent_tasks, agent_audit_log = _agent_panel_context()

    return f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Project Salus Mission Control</title>
      <style>
        body {{
          margin: 0;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          background: #0b0f14;
          color: #e8edf2;
        }}
        header {{
          padding: 28px;
          border-bottom: 1px solid #263241;
          background: #111821;
        }}
        h1 {{
          margin: 0;
          font-size: 30px;
        }}
        h2 {{
          margin-top: 0;
          font-size: 20px;
        }}
        main {{
          padding: 24px;
          display: grid;
          gap: 18px;
        }}
        .grid {{
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
          gap: 14px;
        }}
        .card {{
          background: #141c26;
          border: 1px solid #263241;
          border-radius: 14px;
          padding: 18px;
          box-shadow: 0 8px 24px rgba(0,0,0,.25);
        }}
        .metric {{
          font-size: 34px;
          font-weight: 700;
        }}
        .muted {{
          color: #9fb0c0;
        }}
        .priority {{
          font-size: 18px;
          line-height: 1.45;
        }}
        .table-wrap {{
          overflow-x: auto;
        }}
        table {{
          width: 100%;
          border-collapse: collapse;
          font-size: 14px;
        }}
        th, td {{
          border-bottom: 1px solid #263241;
          padding: 10px;
          text-align: left;
          vertical-align: top;
        }}
        th {{
          color: #9fb0c0;
          font-weight: 600;
        }}
        a {{
          color: #8ab4ff;
        }}
      </style>
    </head>
    <body>
      <header>
        <h1>Project Salus Mission Control</h1>
        <p class="muted">Private command dashboard for missions, SITREPs, AARs, agents, and execution focus.</p>
      </header>


      <nav class="topnav">
        <a href="/command-home">Command Home</a>
        <a href="/command">Command OS</a>
        <a href="/mission-control/ui">Mission Control</a>
        <a href="/command/daily-driver">Daily Driver</a>
        <a href="/command/dashboard-index">Dashboards</a>
        <a href="/command/kernel">Kernel</a>
        <a href="/command/memory">Memory</a>
        <a href="/command/judgment">Judgment</a>
        <a href="/command/teaching-engine">Teaching</a>
        <a href="/command/records">Records</a>
        <a href="/docs">API Docs</a>
      </nav>


        <form method="post" action="/mission-control/logout" style="display:inline;">
          <button type="submit">Logout</button>
        </form>

      <main>
        <section class="grid">
          <div class="card">
            <h2>Active Missions</h2>
            <div class="metric">{len(active_missions)}</div>
          </div>
          <div class="card">
            <h2>Total Missions</h2>
            <div class="metric">{len(missions)}</div>
          </div>
          <div class="card">
            <h2>SITREPs</h2>
            <div class="metric">{len(sitreps)}</div>
          </div>
          <div class="card">
            <h2>AARs</h2>
            <div class="metric">{len(aars)}</div>
          </div>
        </section>

        <section class="card">
          <h2>Commander Priority</h2>
          <p class="priority">{html.escape(top_priority)}</p>
          <p class="muted">Rule: build usable workflow before adding new doctrine.</p>
          <p><a href="/mission-control/brief/latest">Print / Export Latest Brief</a></p>
        </section>

        {_mission_queue(missions)}


        <section class="grid">
          <section class="card">
            <h2>Add Mission</h2>
            <form method="post" action="/mission-control/mission">
              <input name="title" placeholder="Mission title" required>
              <input name="priority" placeholder="Priority: high / medium / low" value="high">
              <input name="status" placeholder="Status" value="active">
              <textarea name="next_action" placeholder="Next action"></textarea>
              <button type="submit">Create Mission</button>
            </form>
          </section>

          <section class="card">
            <h2>Add SITREP</h2>
            <form method="post" action="/mission-control/sitrep">
              <input name="top_priority" placeholder="Top priority" required>
              <input name="blocker" placeholder="Blocker">
              <input name="action_1" placeholder="Action 1">
              <input name="action_2" placeholder="Action 2">
              <input name="action_3" placeholder="Action 3">
              <button type="submit">Submit SITREP</button>
            </form>
          </section>

          <section class="card">
            <h2>Add AAR</h2>
            <form method="post" action="/mission-control/aar">
              <input name="mission_id" placeholder="Mission ID optional">
              <textarea name="what_happened" placeholder="What happened?"></textarea>
              <textarea name="what_worked" placeholder="What worked?"></textarea>
              <textarea name="what_failed" placeholder="What failed?"></textarea>
              <textarea name="lesson" placeholder="Lesson learned"></textarea>
              <textarea name="next_action" placeholder="Next adjustment"></textarea>
              <button type="submit">Capture AAR</button>
            </form>
          </section>
        </section>


        {mc_views.render_agent_task_panel(agent_tasks, agent_audit_log)}


        <section class="card">
          <h2>Daily Commander Brief</h2>
          <p class="muted">Generate a fresh commander brief from current missions, SITREPs, and AARs.</p>
          <form method="post" action="/mission-control/commander-brief">
            <button type="submit">Generate Commander Brief</button>
          </form>
        </section>

        {_table("Daily Commander Briefs", commander_briefs)}

        <section class="card">
          <h2>Daily Workflow Engine</h2>
          <p class="muted">Run the operating rhythm.</p>
          <form method="post" action="/mission-control/daily-workflow/morning_brief">
            <button type="submit">Generate Morning Brief</button>
          </form>
          <form method="post" action="/mission-control/daily-workflow/evening_aar">
            <button type="submit">Generate Evening AAR</button>
          </form>
        </section>

        {_table("Daily Workflow History", daily_workflows)}


        {_table("Missions", missions)}
        {_table("Recent SITREPs", sitreps)}
        {_table("Recent AARs", aars)}
        {_table("Agents", agents)}

        <section class="card">
          <h2>Next Build Step</h2>
          <p>Connect create/update forms so Kyle can add missions, submit SITREPs, and capture AARs from this dashboard.</p>
          <p><a href="/docs">Open API Docs</a></p>
        </section>
      </main>
    </body>
    </html>
    """


@router.get("/api/mission-control/live-status")
def mission_control_live_status():
    with _connect() as conn:
        _ensure_commander_briefs_table(conn)
        _ensure_daily_workflow_table(conn)

        missions = _safe_rows(conn, "missions", 100)
        sitreps = _safe_rows(conn, "sitreps", 10)
        aars = _safe_rows(conn, "aars", 10)
        commander_briefs = _safe_rows(conn, "mission_control_briefs", 5)
        daily_workflows = _safe_rows(conn, "mission_control_daily_workflow", 5)

    active = [
        mission for mission in missions
        if str(mission.get("status", "")).lower() not in {"complete", "completed", "done"}
    ]
    blocked = [
        mission for mission in missions
        if str(mission.get("status", "")).lower() == "blocked"
    ]

    latest_mission = active[0] if active else None
    latest_sitrep = sitreps[0] if sitreps else None
    latest_aar = aars[0] if aars else None
    latest_brief = commander_briefs[0] if commander_briefs else None
    latest_workflow = daily_workflows[0] if daily_workflows else None

    return {
        "status": "ok",
        "active_missions": len(active),
        "blocked_missions": len(blocked),
        "total_missions": len(missions),
        "latest_mission": latest_mission,
        "latest_sitrep": latest_sitrep,
        "latest_aar": latest_aar,
        "latest_brief": latest_brief,
        "latest_workflow": latest_workflow,
    }


@router.post("/mission-control/operator-item")
async def create_operator_item_from_ui(request: Request):
    raw = (await request.body()).decode()
    form = parse_qs(raw)

    mc_service.create_operator_item(
        title=_form_value(form, "title", "Untitled Operator Item"),
        description=_form_value(form, "description", ""),
        queue_type=_form_value(form, "queue_type", "task"),
        status=_form_value(form, "status", "open"),
        priority=_form_value(form, "priority", "medium"),
    )

    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/operator-item/{item_id}/status/{status}")
def update_operator_item_status_from_ui(item_id: int, status: str):
    mc_service.update_operator_item_status(item_id, status)
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/operator-item/{item_id}/convert-to-mission")
def convert_operator_item_to_mission(item_id: int):
    mc_service.convert_operator_item_to_mission(item_id)
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/generate-missions-from-queue")
def generate_missions_from_queue():
    mc_service.generate_missions_from_queue()
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/operator-queue/cleanup")
def cleanup_operator_queue():
    mc_service.cleanup_done_operator_items()
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/agent-task")
async def create_agent_task_from_ui(request: Request):
    raw = (await request.body()).decode()
    form = parse_qs(raw)

    payload_text = _form_value(form, "payload", "")

    mc_service.create_agent_task_from_payload(
        {
            "source": _form_value(form, "source", "manual_commander"),
            "task_type": _form_value(form, "task_type", "general"),
            "title": _form_value(form, "title", "Untitled Agent Task"),
            "risk_level": _form_value(form, "risk_level", "medium"),
            "payload": {"objective": payload_text},
        }
    )

    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/agent-task/{task_id}/approve")
def approve_agent_task_from_ui(task_id: int):
    mc_service.approve_agent_task(task_id, actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/agent-task/{task_id}/reject")
def reject_agent_task_from_ui(task_id: int):
    mc_service.reject_agent_task(task_id, actor="commander_ui", reason="Rejected from Mission Control UI.")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/agent-task/{task_id}/complete")
def complete_agent_task_from_ui(task_id: int):
    mc_service.complete_agent_task(
        task_id,
        result={"message": "Marked complete from Mission Control UI."},
        actor="commander_ui",
    )
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/agent-task/{task_id}/promote-to-mission")
def promote_agent_task_to_mission_from_ui(task_id: int):
    mc_service.promote_agent_task_to_mission(task_id, actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/snapshot")
async def create_snapshot_from_ui(request: Request):
    raw = (await request.body()).decode()
    form = parse_qs(raw)

    mc_service.create_system_snapshot(
        label=_form_value(form, "label", "manual_checkpoint"),
        actor="commander_ui",
    )

    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/snapshot/{snapshot_name}/restore")
def restore_snapshot_from_ui(snapshot_name: str):
    mc_service.restore_system_snapshot(snapshot_name, actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/snapshot/{snapshot_name}/delete")
def delete_snapshot_from_ui(snapshot_name: str):
    mc_service.delete_system_snapshot(snapshot_name, actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/record")
async def create_record_from_ui(request: Request):
    raw = (await request.body()).decode()
    form = parse_qs(raw)

    mc_service.create_record_from_payload(
        {
            "record_type": _form_value(form, "record_type", "note"),
            "title": _form_value(form, "title", "Untitled Record"),
            "content": _form_value(form, "content", ""),
            "source": "commander_ui",
            "tags": _form_value(form, "tags", ""),
        }
    )

    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/daily-loop/{loop_type}")
def create_daily_loop_from_ui(loop_type: str):
    mc_service.create_daily_loop(loop_type=loop_type, actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/connector")
async def upsert_connector_from_ui(request: Request):
    raw = (await request.body()).decode()
    form = parse_qs(raw)

    mc_service.upsert_connector_from_payload(
        {
            "connector_key": _form_value(form, "connector_key", ""),
            "name": _form_value(form, "name", ""),
            "connector_type": _form_value(form, "connector_type", "generic"),
            "status": _form_value(form, "status", "planned"),
            "permission_level": _form_value(form, "permission_level", "external_read"),
            "enabled": _form_value(form, "enabled", "0"),
            "config_summary": _form_value(form, "config_summary", ""),
            "actor": "commander_ui",
        }
    )

    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/connector/{connector_key}/enable")
def enable_connector_from_ui(connector_key: str):
    mc_service.set_connector_enabled(connector_key, True, actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/connector/{connector_key}/disable")
def disable_connector_from_ui(connector_key: str):
    mc_service.set_connector_enabled(connector_key, False, actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/connector/{connector_key}/status/{status}")
def update_connector_status_from_ui(connector_key: str, status: str):
    mc_service.update_connector_status(
        connector_key=connector_key,
        status=status,
        detail=f"Updated from UI to {status}.",
        actor="commander_ui",
    )
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/agent-runtime/run-next")
def run_next_agent_task_from_ui():
    mc_service.run_next_agent_task(actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/agent-runtime/run-batch")
def run_agent_runtime_batch_from_ui():
    mc_service.run_agent_runtime_batch(limit=5, actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/firewall/action")
async def create_external_action_from_ui(request: Request):
    raw = (await request.body()).decode()
    form = parse_qs(raw)

    mc_service.create_external_action_request(
        {
            "connector_key": _form_value(form, "connector_key", "unknown"),
            "action_type": _form_value(form, "action_type", "unknown_action"),
            "title": _form_value(form, "title", "Untitled External Action"),
            "requested_by": "commander_ui",
            "payload": {
                "objective": _form_value(form, "payload", ""),
            },
        }
    )

    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/firewall/action/{action_id}/approve")
def approve_external_action_from_ui(action_id: int):
    mc_service.approve_external_action(action_id, actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/firewall/action/{action_id}/reject")
def reject_external_action_from_ui(action_id: int):
    mc_service.reject_external_action(
        action_id,
        reason="Rejected from Mission Control UI.",
        actor="commander_ui",
    )
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/firewall/action/{action_id}/execute-placeholder")
def execute_external_action_placeholder_from_ui(action_id: int):
    mc_service.execute_external_action_placeholder(action_id, actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/tool-adapter/{adapter_key}/enable")
def enable_tool_adapter_from_ui(adapter_key: str):
    mc_service.set_tool_adapter_enabled(adapter_key, True, actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/tool-adapter/{adapter_key}/disable")
def disable_tool_adapter_from_ui(adapter_key: str):
    mc_service.set_tool_adapter_enabled(adapter_key, False, actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/tool-adapter/{adapter_key}/actions/{action_name}")
async def execute_tool_adapter_action_from_ui(adapter_key: str, action_name: str, request: Request):
    raw = (await request.body()).decode()
    form = parse_qs(raw)

    payload = {
        "path": _form_value(form, "path", "."),
        "actor": "commander_ui",
    }

    mc_service.execute_tool_adapter_action(
        adapter_key=adapter_key,
        action_name=action_name,
        payload=payload,
        actor="commander_ui",
    )

    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/model-provider/reasoning")
async def create_reasoning_request_from_ui(request: Request):
    raw = (await request.body()).decode()
    form = parse_qs(raw)

    mc_service.create_reasoning_request(
        {
            "route_key": _form_value(form, "route_key", "general_reasoning"),
            "prompt": _form_value(form, "prompt", ""),
            "context": _form_value(form, "context", ""),
            "requested_by": "commander_ui",
        }
    )

    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/background-job/sweep")
def run_background_job_sweep_from_ui():
    mc_service.run_background_job_sweep(actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/background-job/{job_key}/run")
def run_background_job_from_ui(job_key: str):
    mc_service.run_background_job(job_key, actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/background-job/{job_key}/enable")
def enable_background_job_from_ui(job_key: str):
    mc_service.set_background_job_enabled(job_key, True, actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.post("/mission-control/background-job/{job_key}/disable")
def disable_background_job_from_ui(job_key: str):
    mc_service.set_background_job_enabled(job_key, False, actor="commander_ui")
    return RedirectResponse("/mission-control/v1", status_code=303)


@router.get("/mission-control/v1", response_class=HTMLResponse)
def mission_control_v1(request: Request) -> str:
    auth_redirect = require_local_dashboard_auth(request)
    if auth_redirect:
        return auth_redirect


    with _connect() as conn:
        _ensure_commander_briefs_table(conn)
        _ensure_daily_workflow_table(conn)

        missions = _safe_rows(conn, "missions", 25)
        sitreps = _safe_rows(conn, "sitreps", 5)
        aars = _safe_rows(conn, "aars", 5)
        commander_briefs = _safe_rows(conn, "mission_control_briefs", 3)
        daily_workflows = _safe_rows(conn, "mission_control_daily_workflow", 3)
        _ensure_operator_queue_table(conn)
        operator_queue = _safe_rows(conn, "mission_control_operator_queue", 12)
        agent_state = mc_service.get_agent_execution_state()
        agent_tasks = agent_state.get("tasks", [])
        agent_audit_log = agent_state.get("audit_log", [])

    active = [
        mission for mission in missions
        if str(mission.get("status", "")).lower() not in {"complete", "completed", "done"}
    ]
    blocked = [
        mission for mission in missions
        if str(mission.get("status", "")).lower() == "blocked"
    ]

    latest_sitrep = sitreps[0] if sitreps else {}
    latest_aar = aars[0] if aars else {}
    latest_brief = commander_briefs[0] if commander_briefs else {}
    latest_workflow = daily_workflows[0] if daily_workflows else {}

    mission_cards = ""
    for mission in active[:6]:
        mission_id = html.escape(str(mission.get("id", "")))
        mission_cards += f"""
        <article class="mission-card">
          <div class="mission-top">
            <strong>{html.escape(str(mission.get("title", "Untitled Mission")))}</strong>
            <span>{html.escape(str(mission.get("priority", "")))}</span>
          </div>
          <p>{html.escape(str(mission.get("next_action", "No next action set.")))}</p>
          <div class="mission-actions">
            <form method="post" action="/mission-control/mission/{mission_id}/status/active"><button>Active</button></form>
            <form method="post" action="/mission-control/mission/{mission_id}/status/blocked"><button>Blocked</button></form>
            <form method="post" action="/mission-control/mission/{mission_id}/status/complete"><button>Complete</button></form>
          </div>
        </article>
        """

    if not mission_cards:
        mission_cards = "<p class='muted'>No active missions. Create one below.</p>"

    agent_tasks, agent_audit_log = _agent_panel_context()

    agent_risk_dashboard = mc_service.get_agent_risk_dashboard()

    system_health = mc_service.get_system_health(request.app)

    snapshot_state = mc_service.get_snapshot_system_state()

    records = mc_service.list_records()
    daily_loops = mc_service.list_daily_loops()
    mvp_readiness = mc_service.get_local_mvp_readiness()

    connector_state = mc_service.get_connector_registry_state()

    agent_runtime_state = mc_service.get_agent_runtime_state()

    firewall_state = mc_service.get_external_action_firewall_state()

    tool_adapter_state = mc_service.get_tool_adapter_state()

    model_provider_state = mc_service.get_model_provider_state()

    background_job_state = mc_service.get_background_job_state()

    return f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Mission Control v1</title>
      <style>
        body {{
          margin: 0;
          font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
          background: #080c11;
          color: #e8edf2;
        }}
        a {{ color: #8ab4ff; text-decoration: none; }}
        .nav {{
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
          padding: 12px 22px;
          background: #0e151d;
          border-bottom: 1px solid #263241;
        }}
        .nav a {{
          border: 1px solid #334960;
          border-radius: 999px;
          padding: 7px 10px;
          color: #cfe3ff;
          background: #121a24;
          font-size: 13px;
        }}
        header {{
          padding: 24px;
          background: linear-gradient(135deg, #111821, #182536);
          border-bottom: 1px solid #263241;
        }}
        h1 {{ margin: 0; font-size: 32px; }}
        h2 {{ margin-top: 0; }}
        main {{
          padding: 20px;
          display: grid;
          grid-template-columns: 1.1fr .9fr;
          gap: 18px;
        }}
        .full {{ grid-column: 1 / -1; }}
        .card {{
          background: #141c26;
          border: 1px solid #263241;
          border-radius: 14px;
          padding: 16px;
          box-shadow: 0 8px 24px rgba(0,0,0,.22);
        }}
        .metrics {{
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
          gap: 12px;
        }}
        .metric {{
          background: #0f1720;
          border: 1px solid #263241;
          border-radius: 12px;
          padding: 14px;
        }}
        .metric strong {{
          display: block;
          font-size: 30px;
        }}
        .muted {{ color: #9fb0c0; }}
        .mission-card {{
          background: #0f1720;
          border: 1px solid #263241;
          border-radius: 12px;
          padding: 12px;
          margin-bottom: 10px;
        }}
        .mission-top {{
          display: flex;
          justify-content: space-between;
          gap: 10px;
        }}
        .mission-top span {{
          color: #9fb0c0;
          font-size: 13px;
        }}
        .mission-actions {{
          display: flex;
          gap: 6px;
          flex-wrap: wrap;
        }}
        form {{ margin: 0; }}
        input, textarea {{
          width: 100%;
          box-sizing: border-box;
          margin: 6px 0;
          padding: 10px;
          border-radius: 8px;
          border: 1px solid #34465a;
          background: #0b0f14;
          color: #e8edf2;
        }}
        textarea {{ min-height: 72px; }}
        button {{
          margin-top: 7px;
          padding: 9px 12px;
          border-radius: 8px;
          border: 1px solid #4d6480;
          background: #1f2c3a;
          color: #e8edf2;
          cursor: pointer;
        }}
        pre {{
          white-space: pre-wrap;
          background: #0b0f14;
          border: 1px solid #263241;
          border-radius: 10px;
          padding: 12px;
          max-height: 280px;
          overflow: auto;
        }}
        .quick {{
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
          gap: 10px;
        }}
        .quick form, .quick a {{
          display: block;
          background: #0f1720;
          border: 1px solid #263241;
          border-radius: 12px;
          padding: 12px;
        }}
        @media (max-width: 900px) {{
          main {{ grid-template-columns: 1fr; }}
        }}
      </style>
    </head>
    <body>
      <nav class="nav">
        <a href="/command-home">Command Home</a>
        <a href="/command">Command OS</a>
        <a href="/mission-control/ui">Classic Mission Control</a>
        <a href="/mission-control/v1">Mission Control v1</a>
        <a href="/mission-control/brief/latest">Print Brief</a>
        <a href="/docs">API Docs</a>
      </nav>

      <header>
        <h1>Mission Control v1</h1>
        <p class="muted">One-screen operating layout for daily execution.</p>
      </header>

      <main>
        {mc_views.render_system_health_panel(system_health)}

        {mc_views.render_snapshot_panel(snapshot_state)}

                                                        {mc_views.render_background_jobs_panel(background_job_state)}

        {mc_views.render_model_provider_panel(model_provider_state)}

        {mc_views.render_tool_adapter_panel(tool_adapter_state)}

        {mc_views.render_external_action_firewall_panel(firewall_state)}

        {mc_views.render_agent_runtime_panel(agent_runtime_state)}

        {mc_views.render_connector_registry_panel(connector_state)}

        {mc_views.render_daily_loop_panel(daily_loops, mvp_readiness)}

        {mc_views.render_records_panel(records)}



        {mc_views.render_agent_risk_dashboard(agent_risk_dashboard)}
        {mc_views.render_agent_task_panel(agent_tasks, agent_audit_log)}

        <section class="card full">
          <div class="metrics">
            <div class="metric"><span>Active Missions</span><strong id="active-count">{len(active)}</strong></div>
            <div class="metric"><span>Blocked</span><strong id="blocked-count">{len(blocked)}</strong></div>
            <div class="metric"><span>SITREPs</span><strong>{len(sitreps)}</strong></div>
            <div class="metric"><span>AARs</span><strong>{len(aars)}</strong></div>
          </div>
          <p id="live-status" class="muted">Live status initializing...</p>
        </section>

        <section class="card">
          <h2>Today Mission Queue</h2>
          {mission_cards}
        </section>


        <section class="card">
          <h2>Operator Inbox</h2>
          <form method="post" action="/mission-control/operator-item">
            <input name="title" placeholder="Task / decision / issue" required>
            <input name="priority" value="high">
            <input name="queue_type" value="task">
            <textarea name="description" placeholder="Details"></textarea>
            <button type="submit">Add to Queue</button>
          </form>
        </section>

        <section class="card">
          <h2>Command Queue</h2>
          <div class="mission-actions" style="margin-bottom:12px;">
            <form method="post" action="/mission-control/generate-missions-from-queue">
              <button type="submit">Generate Missions from Queue</button>
            </form>
            <form method="post" action="/mission-control/operator-queue/cleanup">
              <button type="submit">Cleanup Done Items</button>
            </form>
          </div>
          {_operator_queue_table(operator_queue)}
        </section>


        <section class="card">
          <h2>Quick Actions</h2>
          <div class="quick">
            <form method="post" action="/mission-control/commander-brief">
              <button type="submit">Generate Commander Brief</button>
            </form>
            <form method="post" action="/mission-control/daily-workflow/morning_brief">
              <button type="submit">Morning Brief</button>
            </form>
            <form method="post" action="/mission-control/daily-workflow/evening_aar">
              <button type="submit">Evening AAR</button>
            </form>
            <a href="/mission-control/brief/latest">Print / Export Latest Brief</a>
          </div>

          <h2 style="margin-top:18px;">Create Mission</h2>
          <form method="post" action="/mission-control/mission">
            <input name="title" placeholder="Mission title" required>
            <input name="priority" value="high">
            <input name="status" value="active">
            <textarea name="next_action" placeholder="Next action"></textarea>
            <button type="submit">Create Mission</button>
          </form>
        </section>

        <section class="card">
          <h2>Latest Brief</h2>
          <pre>{html.escape(_value(latest_brief, "brief", default="No commander brief generated."))}</pre>
        </section>

        <section class="card">
          <h2>Latest Workflow</h2>
          <pre>{html.escape(_value(latest_workflow, "content", default="No daily workflow generated."))}</pre>
        </section>

        <section class="card">
          <h2>Submit SITREP</h2>
          <form method="post" action="/mission-control/sitrep">
            <input name="top_priority" placeholder="Top priority" required>
            <input name="blocker" placeholder="Blocker">
            <input name="action_1" placeholder="Action 1">
            <input name="action_2" placeholder="Action 2">
            <input name="action_3" placeholder="Action 3">
            <button type="submit">Submit SITREP</button>
          </form>
          <p class="muted">Latest: {html.escape(_value(latest_sitrep, "top_priority", default="None"))}</p>
        </section>

        <section class="card">
          <h2>Capture AAR</h2>
          <form method="post" action="/mission-control/aar">
            <input name="mission_id" placeholder="Mission name or ID optional">
            <textarea name="what_happened" placeholder="What happened?"></textarea>
            <textarea name="what_worked" placeholder="What worked?"></textarea>
            <textarea name="what_failed" placeholder="What failed?"></textarea>
            <textarea name="lesson" placeholder="Lesson learned"></textarea>
            <textarea name="next_action" placeholder="Next adjustment"></textarea>
            <button type="submit">Capture AAR</button>
          </form>
          <p class="muted">Latest lesson: {html.escape(_value(latest_aar, "lesson_learned", "lesson", default="None"))}</p>
        </section>
      </main>

      <script>
        async function refreshLiveStatus() {{
          try {{
            const response = await fetch("/api/mission-control/live-status");
            const data = await response.json();

            document.getElementById("active-count").textContent = data.active_missions;
            document.getElementById("blocked-count").textContent = data.blocked_missions;

            const latest = data.latest_mission && data.latest_mission.title
              ? data.latest_mission.title
              : "No active mission";

            document.getElementById("live-status").textContent =
              "Live: " + data.status.toUpperCase() +
              " | Active: " + data.active_missions +
              " | Blocked: " + data.blocked_missions +
              " | Focus: " + latest +
              " | Updated: " + new Date().toLocaleTimeString();
          }} catch (error) {{
            document.getElementById("live-status").textContent = "Live status unavailable.";
          }}
        }}

        refreshLiveStatus();
        setInterval(refreshLiveStatus, 15000);
      </script>

    </body>
    </html>
    """
