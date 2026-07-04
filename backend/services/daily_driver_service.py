from __future__ import annotations

import inspect
from typing import Any

from fastapi.responses import HTMLResponse
from backend.services.storage_registry import sync_legacy_globals


def _sync_legacy_globals() -> None:
    """Load shared stores/helpers through the storage registry."""
    sync_legacy_globals(globals())


async def _resolve_result(result: Any) -> Any:
    if inspect.isawaitable(result):
        return await result
    return result


from fastapi.responses import HTMLResponse as _Sprint15HTMLResponse


def _sprint15_safe_count(name: str) -> int:
    value = globals().get(name, [])
    if isinstance(value, dict):
        return len(value)
    if isinstance(value, list):
        return len(value)
    return 0


def _sprint15_empty_state(count: int, empty_message: str, active_message: str) -> str:
    if count <= 0:
        return empty_message
    return active_message


async def sprint15_daily_driver_state() -> Dict[str, Any]:
    missions_count = _sprint15_safe_count("_sprint01_missions")
    daily_briefs_count = _sprint15_safe_count("_sprint01_daily_briefs")
    aars_count = _sprint15_safe_count("_sprint04_aars")
    schoolhouse_courses_count = _sprint15_safe_count("_schoolhouse_courses")
    schoolhouse_sessions_count = _sprint15_safe_count("_schoolhouse_study_sessions")
    charisma_assessments_count = _sprint15_safe_count("_charisma_self_assessments")
    charisma_aars_count = _sprint15_safe_count("_charisma_conversation_aars")

    return {
        "status": "ok",
        "module": "daily_driver_polish",
        "mission": "Make Project Salus usable as Kyle's daily operating system.",
        "start_here": {
            "morning": "Open /command/daily-driver, review state, create today's brief, choose one main mission.",
            "evening": "Open /command/review, review what happened, log AARs, set tomorrow's next action.",
        },
        "morning_workflow": [
            "Check system health.",
            "Create or review today's daily brief.",
            "Pick the top mission.",
            "Run the Schoolhouse daily brief if school is active.",
            "Run one Charisma drill before important communication.",
        ],
        "evening_closeout": [
            "Review missions and saved data.",
            "Log what moved forward.",
            "Log school work or wrong answers.",
            "Log any important conversation AAR.",
            "Set tomorrow's first next action.",
        ],
        "callouts": {
            "missions": {
                "count": missions_count,
                "message": _sprint15_empty_state(
                    missions_count,
                    "No missions recorded yet. Add one mission from /command/ops.",
                    "Mission data exists. Review it from /command/review.",
                ),
            },
            "daily_briefs": {
                "count": daily_briefs_count,
                "message": _sprint15_empty_state(
                    daily_briefs_count,
                    "No daily brief recorded yet. Create today's brief from /command/ops.",
                    "Daily brief history exists.",
                ),
            },
            "schoolhouse": {
                "courses": schoolhouse_courses_count,
                "study_sessions": schoolhouse_sessions_count,
                "message": _sprint15_empty_state(
                    schoolhouse_courses_count,
                    "No Schoolhouse courses recorded yet. Add your current WGU course from /command/ops.",
                    "Schoolhouse is active. Continue study sessions and wrong-answer review.",
                ),
            },
            "charisma": {
                "self_assessments": charisma_assessments_count,
                "conversation_aars": charisma_aars_count,
                "message": _sprint15_empty_state(
                    charisma_assessments_count + charisma_aars_count,
                    "No Charisma records yet. Run one drill or self-assessment.",
                    "Charisma training data exists. Review communication patterns.",
                ),
            },
            "aars": {
                "count": aars_count,
                "message": _sprint15_empty_state(
                    aars_count,
                    "No AARs recorded yet. Close today with a short after-action review.",
                    "AAR history exists. Use it to improve tomorrow.",
                ),
            },
        },
        "primary_pages": {
            "daily_driver": "/command/daily-driver",
            "ops": "/command/ops",
            "review": "/command/review",
            "home": "/command/home",
            "integrated": "/command/integrated",
        },
        "next_action": "Use /command/ops to create records, then /command/review to inspect them.",
    }


async def sprint15_daily_driver_page() -> _Sprint15HTMLResponse:
    html = """
    <!doctype html>
    <html>
      <head>
        <title>Project Salus — Daily Driver</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            background: #07111f;
            color: #f4f7fb;
            margin: 0;
            padding: 32px;
          }
          h1, h2 {
            color: #d7b46a;
          }
          .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 18px;
          }
          .panel {
            border: 1px solid #28405f;
            border-radius: 12px;
            padding: 20px;
            background: #0d1c2f;
            margin-bottom: 18px;
          }
          a.button, button {
            display: inline-block;
            background: #d7b46a;
            color: #07111f;
            border: none;
            padding: 11px 15px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
            text-decoration: none;
            margin: 5px 5px 5px 0;
          }
          pre {
            white-space: pre-wrap;
            background: #081525;
            padding: 14px;
            border-radius: 8px;
            border: 1px solid #28405f;
            max-height: 380px;
            overflow: auto;
          }
          .muted {
            color: #aab7c7;
          }
          .big {
            font-size: 18px;
            line-height: 1.45;
          }
        </style>
      </head>
      <body>
        <h1>Project Salus — Daily Driver</h1>
        <p class="muted">One-page command flow for starting and closing the day.</p>

        <div class="panel">
          <h2>Start Here</h2>
          <p class="big"><strong>Morning:</strong> create today’s brief, pick one main mission, then execute.</p>
          <p class="big"><strong>Evening:</strong> review saved data, log AARs, and set tomorrow’s first action.</p>
          <a class="button" href="/command/ops">Open Operational Dashboard</a>
          <a class="button" href="/command/review">Open Review History</a>
          <a class="button" href="/command/home">Open Command Home</a>
          <button onclick="loadDailyDriver()">Refresh Daily Driver State</button>
        </div>

        <div class="grid">
          <div class="panel">
            <h2>Morning Workflow</h2>
            <ol>
              <li>Check health.</li>
              <li>Create or review today's daily brief.</li>
              <li>Pick the top mission.</li>
              <li>Run Schoolhouse if school is active.</li>
              <li>Run one Charisma drill before important communication.</li>
            </ol>
          </div>

          <div class="panel">
            <h2>Evening Closeout</h2>
            <ol>
              <li>Review mission progress.</li>
              <li>Log school work or wrong answers.</li>
              <li>Log important conversation AARs.</li>
              <li>Record the day’s AAR.</li>
              <li>Set tomorrow’s first next action.</li>
            </ol>
          </div>

          <div class="panel">
            <h2>Mission Callout</h2>
            <pre id="missions">Loading...</pre>
          </div>

          <div class="panel">
            <h2>Schoolhouse Callout</h2>
            <pre id="schoolhouse">Loading...</pre>
          </div>

          <div class="panel">
            <h2>Charisma Drill Callout</h2>
            <pre id="charisma">Loading...</pre>
          </div>

          <div class="panel">
            <h2>AAR Callout</h2>
            <pre id="aars">Loading...</pre>
          </div>
        </div>

        <div class="panel">
          <h2>Full Daily Driver State</h2>
          <pre id="state">Loading...</pre>
        </div>

        <script>
          async function getJson(path) {
            const res = await fetch(path);
            return await res.json();
          }

          function show(id, data) {
            document.getElementById(id).textContent = JSON.stringify(data, null, 2);
          }

          async function loadDailyDriver() {
            const state = await getJson("/api/command/daily-driver-state");
            show("state", state);
            show("missions", state.callouts.missions);
            show("schoolhouse", state.callouts.schoolhouse);
            show("charisma", state.callouts.charisma);
            show("aars", state.callouts.aars);
          }

          loadDailyDriver();
        </script>
      </body>
    </html>
    """
    return _Sprint15HTMLResponse(content=html)



async def get_daily_driver_state() -> Any:
    _sync_legacy_globals()
    return await _resolve_result(sprint15_daily_driver_state())


async def get_daily_driver_page() -> Any:
    _sync_legacy_globals()
    return await _resolve_result(sprint15_daily_driver_page())
