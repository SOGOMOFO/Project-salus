from __future__ import annotations

import html
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from urllib.parse import parse_qs


router = APIRouter(tags=["mission-control-ui"])


def _db_path() -> Path:
    return Path(__file__).resolve().parents[2] / "salus.db"


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def _table_exists(conn: sqlite3.Connection, table: str) -> bool:
    row = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table,),
    ).fetchone()
    return row is not None


def _safe_rows(conn: sqlite3.Connection, table: str, limit: int = 10) -> list[dict[str, Any]]:
    if not _table_exists(conn, table):
        return []

    try:
        rows = conn.execute(f"SELECT * FROM {table} ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    except sqlite3.OperationalError:
        rows = conn.execute(f"SELECT * FROM {table} LIMIT ?", (limit,)).fetchall()

    return [dict(row) for row in rows]


def _ensure_commander_briefs_table(conn: sqlite3.Connection) -> None:
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
    conn.commit()


def _value(row: dict[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return default


def _build_commander_brief(
    missions: list[dict[str, Any]],
    sitreps: list[dict[str, Any]],
    aars: list[dict[str, Any]],
) -> str:
    open_missions = [
        mission for mission in missions
        if str(mission.get("status", "")).lower() not in {"complete", "completed", "done"}
    ]

    blocked_missions = [
        mission for mission in missions
        if str(mission.get("status", "")).lower() == "blocked"
    ]

    latest_sitrep = sitreps[0] if sitreps else None
    latest_aar = aars[0] if aars else None

    next_action = "Create or update the highest-priority active mission."
    if open_missions:
        next_action = _value(
            open_missions[0],
            "next_action",
            "title",
            default="Review the highest-priority active mission.",
        )

    lines = [
        "PROJECT SALUS DAILY COMMANDER BRIEF",
        "",
        "Operating Status: ACTIVE",
        f"Open Missions: {len(open_missions)}",
        f"Blocked Missions: {len(blocked_missions)}",
        f"Total Missions Reviewed: {len(missions)}",
        "",
        "Top Mission Focus:",
        _value(open_missions[0], "title", default="No active mission found.") if open_missions else "No active mission found.",
        "",
        "Latest SITREP:",
        _value(latest_sitrep, "top_priority", default="No SITREP available.") if latest_sitrep else "No SITREP available.",
        "",
        "Latest AAR Lesson:",
        _value(latest_aar, "lesson_learned", "lesson", default="No AAR lesson captured.") if latest_aar else "No AAR available.",
        "",
        "Next Recommended Action:",
        next_action,
        "",
        "Commander Rule:",
        "Build usable workflow before adding new doctrine.",
    ]

    return "\n".join(str(line) if line is not None else "" for line in lines)


def _cell(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value))


def _ensure_daily_workflow_table(conn: sqlite3.Connection) -> None:
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
    conn.commit()


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


def _insert_dynamic(table: str, values: dict[str, Any]) -> None:
    with _connect() as conn:
        if not _table_exists(conn, table):
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
    </body>
    </html>
    """


@router.get("/mission-control/ui", response_class=HTMLResponse)
def mission_control_ui() -> str:
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
