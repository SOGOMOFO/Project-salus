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


def render_agent_task_panel(tasks: list[dict[str, Any]], audit_log: list[dict[str, Any]]) -> str:
    task_html = render_agent_task_cards(tasks)
    audit_html = render_agent_audit_cards(audit_log)

    return f"""
        <section class="card">
          <h2>Agent Execution Registry</h2>
          <p class="muted">Approval-gated agent task control for future Salus automation.</p>

          <form method="post" action="/mission-control/agent-task">
            <input name="title" placeholder="Agent task title" required>
            <input name="source" value="manual_commander">
            <input name="task_type" value="general">
            <select name="risk_level">
              <option value="low">low</option>
              <option value="medium" selected>medium</option>
              <option value="high">high</option>
              <option value="critical">critical</option>
            </select>
            <textarea name="payload" placeholder="Task payload / objective"></textarea>
            <button type="submit">Create Agent Task</button>
          </form>
        </section>

        <section class="card">
          <h2>Agent Tasks</h2>
          {task_html}
        </section>

        <section class="card">
          <h2>Agent Audit Log</h2>
          {audit_html}
        </section>
    """


def render_agent_task_cards(tasks: list[dict[str, Any]]) -> str:
    if not tasks:
        return "<p class='muted'>No agent tasks recorded.</p>"

    body = ""

    for task in tasks[:20]:
        task_id = cell(task.get("id", ""))
        title = cell(task.get("title", "Untitled Agent Task"))
        source = cell(task.get("source", "unknown"))
        task_type = cell(task.get("task_type", "general"))
        status = cell(task.get("status", "unknown"))
        risk_level = cell(task.get("risk_level", "medium"))
        approved = cell(task.get("approved", "0"))
        requires_approval = cell(task.get("requires_approval", "1"))

        body += f"""
        <article class="mission-card">
          <div class="mission-top">
            <strong>{title}</strong>
            <span>{risk_level}</span>
          </div>
          <p class="muted">Source: {source} | Type: {task_type}</p>
          <p>Status: {status} | Requires approval: {requires_approval} | Approved: {approved}</p>
          <div class="mission-actions">
            <form method="post" action="/mission-control/agent-task/{task_id}/approve"><button>Approve</button></form>
            <form method="post" action="/mission-control/agent-task/{task_id}/reject"><button>Reject</button></form>
            <form method="post" action="/mission-control/agent-task/{task_id}/complete"><button>Mark Complete</button></form>
            <form method="post" action="/mission-control/agent-task/{task_id}/promote-to-mission"><button>Promote to Mission</button></form>
          </div>
        </article>
        """

    return body


def render_agent_audit_cards(audit_log: list[dict[str, Any]]) -> str:
    if not audit_log:
        return "<p class='muted'>No audit events recorded.</p>"

    body = ""

    for event in audit_log[:15]:
        actor = cell(event.get("actor", "system"))
        action = cell(event.get("action", "unknown_action"))
        target_type = cell(event.get("target_type", "unknown_target"))
        target_id = cell(event.get("target_id", ""))
        detail = cell(event.get("detail", ""))

        body += f"""
        <article class="mission-card">
          <strong>{action}</strong>
          <p class="muted">Actor: {actor} | Target: {target_type}:{target_id}</p>
          <p>{detail}</p>
        </article>
        """

    return body


def render_agent_risk_dashboard(dashboard: dict[str, Any]) -> str:
    counts = dashboard.get("counts", {})
    by_risk = dashboard.get("by_risk", {})
    recommendation = cell(dashboard.get("recommended_action", "Review agent execution posture."))
    posture = cell(dashboard.get("posture", "unknown"))

    return f"""
        <section class="card">
          <h2>Agent Risk Dashboard</h2>
          <p class="muted">Posture: {posture}</p>
          <section class="grid">
            <div class="card"><h2>Total Tasks</h2><div class="metric">{cell(counts.get("total", 0))}</div></div>
            <div class="card"><h2>Pending Approval</h2><div class="metric">{cell(counts.get("pending_approval", 0))}</div></div>
            <div class="card"><h2>Executable</h2><div class="metric">{cell(counts.get("executable", 0))}</div></div>
            <div class="card"><h2>Blocked</h2><div class="metric">{cell(counts.get("blocked", 0))}</div></div>
          </section>
          <p>Low: {cell(by_risk.get("low", 0))} | Medium: {cell(by_risk.get("medium", 0))} | High: {cell(by_risk.get("high", 0))} | Critical: {cell(by_risk.get("critical", 0))}</p>
          <p><strong>Recommended Action:</strong> {recommendation}</p>
        </section>
    """


def render_system_health_panel(health: dict[str, Any]) -> str:
    checks = health.get("checks", {})
    contract = health.get("contract", {})
    counts = contract.get("counts", {})
    risk = health.get("risk", {})

    check_lines = ""
    for name, passed in checks.items():
        check_lines += f"<p>{cell(name)}: {'PASS' if passed else 'FAIL'}</p>"

    return f"""
        <section class="card">
          <h2>System Health</h2>
          <p class="muted">Posture: {cell(health.get("posture", "unknown"))}</p>
          <section class="grid">
            <div class="card"><h2>Total Routes</h2><div class="metric">{cell(counts.get("total_routes", 0))}</div></div>
            <div class="card"><h2>MC Routes</h2><div class="metric">{cell(counts.get("mission_control_routes", 0))}</div></div>
            <div class="card"><h2>MC APIs</h2><div class="metric">{cell(counts.get("mission_control_api_routes", 0))}</div></div>
            <div class="card"><h2>MC UI</h2><div class="metric">{cell(counts.get("mission_control_ui_routes", 0))}</div></div>
          </section>
          <p><strong>Risk Posture:</strong> {cell(risk.get("posture", "unknown"))}</p>
          <p><strong>Recommended Action:</strong> {cell(risk.get("recommended_action", "Review system state."))}</p>
          <div>{check_lines}</div>
          <p><a href="/api/mission-control/health">Health JSON</a> | <a href="/api/mission-control/contract">API Contract</a> | <a href="/api/mission-control/routes">Route Inventory</a></p>
        </section>
    """


def render_snapshot_panel(snapshot_state: dict[str, Any]) -> str:
    snapshots = snapshot_state.get("snapshots", [])
    latest = snapshot_state.get("latest_snapshot") or {}
    latest_name = latest.get("snapshot_name", "None")

    rows = ""

    for snapshot in snapshots[:10]:
        name = cell(snapshot.get("snapshot_name", "unknown"))
        size = cell(snapshot.get("size_bytes", 0))
        created = cell(snapshot.get("created_at", ""))
        db_exists = cell(snapshot.get("database_exists", False))

        rows += f"""
          <tr>
            <td>{name}</td>
            <td>{created}</td>
            <td>{size}</td>
            <td>{db_exists}</td>
            <td>
              <form method="post" action="/mission-control/snapshot/{name}/restore">
                <button type="submit">Restore</button>
              </form>
              <form method="post" action="/mission-control/snapshot/{name}/delete">
                <button type="submit">Delete</button>
              </form>
            </td>
          </tr>
        """

    if not rows:
        rows = "<tr><td colspan='5'>No snapshots created yet.</td></tr>"

    return f"""
        <section class="card">
          <h2>Snapshot Backup System</h2>
          <p class="muted">{cell(snapshot_state.get("recommended_action", ""))}</p>
          <section class="grid">
            <div class="card"><h2>Snapshots</h2><div class="metric">{cell(snapshot_state.get("snapshot_count", 0))}</div></div>
            <div class="card"><h2>Latest</h2><p>{cell(latest_name)}</p></div>
          </section>

          <form method="post" action="/mission-control/snapshot">
            <input name="label" placeholder="Snapshot label" value="manual_checkpoint">
            <button type="submit">Create Snapshot</button>
          </form>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Snapshot</th>
                  <th>Created</th>
                  <th>Size</th>
                  <th>DB Exists</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>{rows}</tbody>
            </table>
          </div>

          <p>
            <a href="/api/mission-control/snapshots">Snapshots JSON</a>
          </p>
        </section>
    """
