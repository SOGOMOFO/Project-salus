from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["command-daily-driver"])

CountProvider = Callable[[str], int]


DAILY_DRIVER_ROUTE_MANIFEST = {
    "api": "/api/command/daily-driver-state",
    "page": "/command/daily-driver",
    "module": "daily_driver_polish",
}


def default_count_provider(_: str) -> int:
    return 0


def build_daily_driver_payload(count_provider: CountProvider = default_count_provider) -> dict[str, Any]:
    counts = {
        "missions": count_provider("_sprint01_missions"),
        "daily_briefs": count_provider("_sprint01_daily_briefs"),
        "aars": count_provider("_sprint04_aars"),
        "schoolhouse_courses": count_provider("_schoolhouse_courses"),
        "schoolhouse_study_sessions": count_provider("_schoolhouse_study_sessions"),
        "charisma_self_assessments": count_provider("_charisma_self_assessments"),
        "charisma_conversation_aars": count_provider("_charisma_conversation_aars"),
    }

    return {
        "status": "ok",
        "module": "daily_driver_polish",
        "page": "/command/daily-driver",
        "primary_daily_page": "/command/workflows",
        "readiness_page": "/command/readiness",
        "navigation_page": "/command/navigation",
        "dashboard_index_page": "/command/dashboard-index",
        "counts": counts,
        "morning_sequence": [
            {
                "step": 1,
                "label": "Open workflows",
                "href": "/command/workflows",
                "intent": "Run the morning sequence.",
            },
            {
                "step": 2,
                "label": "Check readiness",
                "href": "/command/readiness",
                "intent": "Confirm system and operating readiness.",
            },
            {
                "step": 3,
                "label": "Create daily brief",
                "href": "/command/ops",
                "intent": "Set commander intent and priority mission.",
            },
        ],
        "evening_sequence": [
            {
                "step": 1,
                "label": "Review records",
                "href": "/command/review",
                "intent": "Review what happened today.",
            },
            {
                "step": 2,
                "label": "Clean records if needed",
                "href": "/command/records",
                "intent": "Archive or delete bad demo records.",
            },
            {
                "step": 3,
                "label": "Close AAR",
                "href": "/command/ops",
                "intent": "Capture lessons and tomorrow’s first action.",
            },
        ],
        "next_action": "Open /command/workflows and run the current checklist.",
    }


def render_daily_driver_html() -> str:
    return """
    <!doctype html>
    <html>
      <head>
        <title>Project Salus — Daily Driver</title>
      </head>
      <body>
        <h1>Project Salus — Daily Driver</h1>
        <p>Fast daily command page for morning start and evening closeout.</p>

        <h2>Navigation</h2>
        <a href="/command/workflows">Workflows</a>
        <a href="/command/readiness">Readiness</a>
        <a href="/command/navigation">Navigation</a>
        <a href="/command/dashboard-index">Dashboard Index</a>
        <a href="/command/ops">Ops</a>
        <a href="/command/review">Review</a>
        <a href="/command/records">Records</a>

        <h2>Morning Sequence</h2>
        <pre id="morning">Loading morning sequence...</pre>

        <h2>Evening Sequence</h2>
        <pre id="evening">Loading evening sequence...</pre>

        <h2>Daily Driver State</h2>
        <pre id="state">Loading daily driver...</pre>

        <script>
          fetch("/api/command/daily-driver-state")
            .then(response => response.json())
            .then(data => {
              document.getElementById("morning").textContent = JSON.stringify(data.morning_sequence, null, 2);
              document.getElementById("evening").textContent = JSON.stringify(data.evening_sequence, null, 2);
              document.getElementById("state").textContent = JSON.stringify(data, null, 2);
            });
        </script>
      </body>
    </html>
    """

from backend.services.legacy_route_adapter import call_main_handler

@router.get("/api/command/daily-driver-state")
async def sprint26_daily_driver_sprint15_daily_driver_state_bridge() -> Any:
    return await call_main_handler("sprint15_daily_driver_state")


@router.get("/command/daily-driver", response_class=HTMLResponse)
async def sprint26_daily_driver_sprint15_daily_driver_page_bridge() -> Any:
    return await call_main_handler("sprint15_daily_driver_page")
