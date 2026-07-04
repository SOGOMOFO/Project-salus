from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(tags=["command-workflows"])

CountProvider = Callable[[str], int]


WORKFLOWS_ROUTE_MANIFEST = {
    "morning_api": "/api/workflows/morning",
    "evening_api": "/api/workflows/evening",
    "today_api": "/api/workflows/today",
    "page": "/command/workflows",
    "module": "daily_workflow_automation",
}


def default_count_provider(_: str) -> int:
    return 0


def workflow_link(label: str, href: str, action: str, reason: str) -> dict[str, Any]:
    return {
        "label": label,
        "href": href,
        "action": action,
        "reason": reason,
    }


def operational_counts(count_provider: CountProvider = default_count_provider) -> dict[str, int]:
    return {
        "missions": count_provider("_sprint01_missions"),
        "daily_briefs": count_provider("_sprint01_daily_briefs"),
        "aars": count_provider("_sprint04_aars"),
        "schoolhouse_courses": count_provider("_schoolhouse_courses"),
        "schoolhouse_study_sessions": count_provider("_schoolhouse_study_sessions"),
        "charisma_self_assessments": count_provider("_charisma_self_assessments"),
        "charisma_conversation_aars": count_provider("_charisma_conversation_aars"),
    }


def build_morning_workflow(count_provider: CountProvider = default_count_provider) -> dict[str, Any]:
    counts = operational_counts(count_provider)

    checklist = [
        workflow_link("Check system health", "/api/command/health", "Confirm Project Salus is running.", "System status comes before mission execution."),
        workflow_link("Open daily driver", "/command/daily-driver", "Review the daily state and callouts.", "This is the fastest command view."),
        workflow_link("Create or review daily brief", "/command/ops", "Set commander intent, priorities, risks, and next actions.", "This frames the day."),
        workflow_link("Choose one main mission", "/command/ops", "Pick the single highest-leverage mission.", "One main mission prevents scattered execution."),
        workflow_link("Run Schoolhouse block", "/command/ops", "Log one focused study session if school is active today.", "School is an active capability mission."),
        workflow_link("Run Charisma drill", "/api/skills/charisma/daily-drill", "Complete one communication drill before important conversations.", "Communication skill compounds across school, business, and family."),
    ]

    return {
        "status": "ok",
        "workflow": "morning",
        "module": "daily_workflow_automation",
        "intent": "Start the day with command clarity and one main mission.",
        "estimated_minutes": 10,
        "counts": counts,
        "checklist": checklist,
        "first_action": "Open /command/daily-driver.",
        "primary_page": "/command/workflows",
    }


def build_evening_workflow(count_provider: CountProvider = default_count_provider) -> dict[str, Any]:
    counts = operational_counts(count_provider)

    checklist = [
        workflow_link("Open review dashboard", "/command/review", "Review missions, Schoolhouse data, Charisma records, and AARs.", "Review turns activity into learning."),
        workflow_link("Review records", "/command/records", "Archive or delete bad/demo records if needed.", "Clean data keeps Salus useful."),
        workflow_link("Close mission loop", "/command/review", "Identify what moved, what stalled, and tomorrow’s next action.", "This prevents drift."),
        workflow_link("Close Schoolhouse loop", "/command/ops", "Log study work, weak areas, or wrong answers.", "Learning requires evidence and repetition."),
        workflow_link("Close communication loop", "/command/ops", "Log any important conversation AAR.", "Charisma improves through review."),
        workflow_link("Log AAR", "/command/ops", "Record the day’s lesson and tomorrow’s first action.", "The AAR converts today into better judgment."),
    ]

    return {
        "status": "ok",
        "workflow": "evening",
        "module": "daily_workflow_automation",
        "intent": "Close the day, capture lessons, and set tomorrow’s first action.",
        "estimated_minutes": 10,
        "counts": counts,
        "checklist": checklist,
        "final_action": "Set tomorrow’s first next action.",
        "primary_page": "/command/workflows",
    }


def build_today_workflows(count_provider: CountProvider = default_count_provider) -> dict[str, Any]:
    return {
        "status": "ok",
        "module": "daily_workflow_automation",
        "page": "/command/workflows",
        "morning": build_morning_workflow(count_provider),
        "evening": build_evening_workflow(count_provider),
        "recommended_use": {
            "morning": "Run before starting work.",
            "evening": "Run before shutting down.",
        },
    }


def render_workflows_html() -> str:
    return """
    <!doctype html>
    <html>
      <head>
        <title>Project Salus — Daily Workflows</title>
      </head>
      <body>
        <h1>Project Salus — Daily Workflow Automation</h1>
        <p>Guided morning and evening operating sequence.</p>

        <h2>Navigation</h2>
        <a href="/command/daily-driver">Daily Driver</a>
        <a href="/command/ops">Ops Dashboard</a>
        <a href="/command/review">Review Dashboard</a>
        <a href="/command/records">Record Management</a>
        <a href="/command/home">Command Home</a>
        <a href="/command/navigation">Navigation Hub</a>
        <a href="/command/readiness">Readiness</a>

        <h2>Morning Workflow</h2>
        <pre id="morningRaw">Loading...</pre>

        <h2>Evening Closeout</h2>
        <pre id="eveningRaw">Loading...</pre>

        <h2>Full Workflow State</h2>
        <pre id="state">Loading...</pre>

        <script>
          fetch("/api/workflows/today")
            .then(response => response.json())
            .then(data => {
              document.getElementById("morningRaw").textContent = JSON.stringify(data.morning, null, 2);
              document.getElementById("eveningRaw").textContent = JSON.stringify(data.evening, null, 2);
              document.getElementById("state").textContent = JSON.stringify(data, null, 2);
            });
        </script>
      </body>
    </html>
    """


@router.get("/api/workflows/morning")
async def morning_workflow_api() -> dict[str, Any]:
    return build_morning_workflow()


@router.get("/api/workflows/evening")
async def evening_workflow_api() -> dict[str, Any]:
    return build_evening_workflow()


@router.get("/api/workflows/today")
async def today_workflows_api() -> dict[str, Any]:
    return build_today_workflows()


@router.get("/command/workflows", response_class=HTMLResponse)
async def workflows_page() -> HTMLResponse:
    return HTMLResponse(content=render_workflows_html())
