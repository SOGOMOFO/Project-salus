from __future__ import annotations

import html
import sqlite3
from pathlib import Path
from typing import Any

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


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


def _cell(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value))


def _table(title: str, rows: list[dict[str, Any]]) -> str:
    if not rows:
        return f"""
        <section class="card">
          <h2>{html.escape(title)}</h2>
          <p class="muted">No records yet.</p>
        </section>
        """

    columns = list(rows[0].keys())
    headers = "".join(f"<th>{html.escape(col)}</th>" for col in columns)

    body = ""
    for row in rows:
        body += "<tr>" + "".join(f"<td>{_cell(row.get(col))}</td>" for col in columns) + "</tr>"

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


@router.get("/mission-control/ui", response_class=HTMLResponse)
def mission_control_ui() -> str:
    with _connect() as conn:
        missions = _safe_rows(conn, "missions", 10)
        sitreps = _safe_rows(conn, "sitreps", 10)
        aars = _safe_rows(conn, "aars", 10)
        agents = _safe_rows(conn, "agents", 10)

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
        </section>

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
