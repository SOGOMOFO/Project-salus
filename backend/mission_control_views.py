from __future__ import annotations

import html
from typing import Any


def cell(value: Any) -> str:
    if value is None:
        return ""
    return html.escape(str(value))


def render_operator_queue_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<p class='muted'>No operator queue items.</p>"

    body = ""

    for row in rows:
        item_id = cell(row.get("id", ""))
        title = cell(row.get("title", "Untitled"))
        description = cell(row.get("description", ""))
        status = cell(row.get("status", ""))
        priority = cell(row.get("priority", ""))
        queue_type = cell(row.get("queue_type", ""))

        body += f"""
        <article class="mission-card">
          <div class="mission-top">
            <strong>{title}</strong>
            <span>{priority}</span>
          </div>
          <p>{description}</p>
          <p class="muted">Type: {queue_type} | Status: {status}</p>
          <div class="mission-actions">
            <form method="post" action="/mission-control/operator-item/{item_id}/status/in_progress"><button>In Progress</button></form>
            <form method="post" action="/mission-control/operator-item/{item_id}/status/blocked"><button>Blocked</button></form>
            <form method="post" action="/mission-control/operator-item/{item_id}/status/done"><button>Done</button></form>
            <form method="post" action="/mission-control/operator-item/{item_id}/convert-to-mission"><button>Convert to Mission</button></form>
          </div>
        </article>
        """

    return body


def render_queue_controls() -> str:
    return """
    <div class="mission-actions" style="margin-bottom:12px;">
      <form method="post" action="/mission-control/generate-missions-from-queue">
        <button type="submit">Generate Missions from Queue</button>
      </form>
      <form method="post" action="/mission-control/operator-queue/cleanup">
        <button type="submit">Cleanup Done Items</button>
      </form>
    </div>
    """


def render_live_status_script() -> str:
    return """
      <script>
        async function refreshLiveStatus() {
          try {
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
          } catch (error) {
            document.getElementById("live-status").textContent = "Live status unavailable.";
          }
        }

        refreshLiveStatus();
        setInterval(refreshLiveStatus, 15000);
      </script>
    """


def render_operator_inbox_panel() -> str:
    return """
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
    """
