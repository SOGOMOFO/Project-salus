from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(tags=["command-navigation"])


NAVIGATION_ROUTE_MANIFEST = {
    "api": "/api/command/navigation",
    "page": "/command/navigation",
    "module": "navigation_unification_ux_cleanup",
}


def navigation_groups() -> dict[str, Any]:
    return {
        "daily_operations": [
            {
                "label": "Daily Workflows",
                "href": "/command/workflows",
                "description": "Guided morning and evening workflow. This is the primary daily operating guide.",
                "priority": 1,
            },
            {
                "label": "Daily Driver",
                "href": "/command/daily-driver",
                "description": "One-page morning and evening command flow.",
                "priority": 2,
            },
            {
                "label": "Operational Dashboard",
                "href": "/command/ops",
                "description": "Create daily briefs, missions, school entries, and charisma AARs.",
                "priority": 3,
            },
            {
                "label": "Daily Mode",
                "href": "/command/daily",
                "description": "Earlier daily-use mode page.",
                "priority": 4,
            },
        ],
        "review_and_records": [
            {
                "label": "Review Dashboard",
                "href": "/command/review",
                "description": "Review stored missions, Schoolhouse data, Charisma data, and AAR history.",
                "priority": 1,
            },
            {
                "label": "Record Management",
                "href": "/command/records",
                "description": "Archive or delete bad/demo records.",
                "priority": 2,
            },
            {
                "label": "Integrated Dashboard",
                "href": "/command/integrated",
                "description": "Integrated state view for Daily Use, Schoolhouse, and Charisma.",
                "priority": 3,
            },
        ],
        "capability_modules": [
            {
                "label": "Schoolhouse Status",
                "href": "/api/schoolhouse/status",
                "description": "Learning coach module status.",
                "priority": 1,
            },
            {
                "label": "Schoolhouse Daily Brief",
                "href": "/api/schoolhouse/daily-brief",
                "description": "School-focused daily brief.",
                "priority": 2,
            },
            {
                "label": "Charisma Status",
                "href": "/api/skills/charisma",
                "description": "Communication and charisma skill module status.",
                "priority": 3,
            },
            {
                "label": "Charisma Daily Drill",
                "href": "/api/skills/charisma/daily-drill",
                "description": "Daily communication drill.",
                "priority": 4,
            },
        ],
        "system": [
            {
                "label": "Command Home",
                "href": "/command/home",
                "description": "Project Salus command launcher.",
                "priority": 1,
            },
            {
                "label": "Health",
                "href": "/api/command/health",
                "description": "System health and page inventory.",
                "priority": 2,
            },
            {
                "label": "Navigation API",
                "href": "/api/command/navigation",
                "description": "Central navigation inventory.",
                "priority": 3,
            },
        ],
    }


def build_navigation_payload() -> dict[str, Any]:
    primary_pages = {
        "workflows": "/command/workflows",
        "daily_driver": "/command/daily-driver",
        "command_home": "/command/home",
        "ops": "/command/ops",
        "review": "/command/review",
        "records": "/command/records",
        "integrated": "/command/integrated",
        "daily": "/command/daily",
        "navigation": "/command/navigation",
        "readiness": "/command/readiness",
        "dashboard_index": "/command/dashboard-index",
    }

    return {
        "status": "ok",
        "module": "navigation_unification_ux_cleanup",
        "primary_daily_page": "/command/workflows",
        "primary_pages": primary_pages,
        "groups": navigation_groups(),
        "recommended_start": {
            "morning": "/command/workflows",
            "daily_execution": "/command/daily-driver",
            "data_entry": "/command/ops",
            "review": "/command/review",
            "cleanup": "/command/records",
            "status": "/command/readiness",
            "index": "/command/dashboard-index",
        },
        "next_action": "Use /command/workflows as the primary daily operating guide.",
    }


def render_navigation_html() -> str:
    return """
    <!doctype html>
    <html>
      <head>
        <title>Project Salus — Navigation Hub</title>
      </head>
      <body>
        <h1>Project Salus — Navigation Hub</h1>
        <p>One place to reach every major Project Salus page.</p>

        <h2>Start Here</h2>
        <a href="/command/workflows">Primary Daily Guide</a>
        <a href="/command/daily-driver">Daily Driver</a>
        <a href="/command/ops">Operational Dashboard</a>
        <a href="/command/review">Review Dashboard</a>
        <a href="/command/records">Record Management</a>
        <a href="/command/readiness">Readiness</a>
        <a href="/command/dashboard-index">Dashboard Index</a>

        <h2>Daily Operations</h2>
        <pre id="daily_operations">Loading...</pre>

        <h2>Review and Records</h2>
        <pre id="review_and_records">Loading...</pre>

        <h2>Capability Modules</h2>
        <pre id="capability_modules">Loading...</pre>

        <h2>System</h2>
        <pre id="system">Loading...</pre>

        <h2>Navigation State</h2>
        <pre id="state">Loading...</pre>

        <script>
          fetch("/api/command/navigation")
            .then(response => response.json())
            .then(data => {
              document.getElementById("daily_operations").textContent = JSON.stringify(data.groups.daily_operations, null, 2);
              document.getElementById("review_and_records").textContent = JSON.stringify(data.groups.review_and_records, null, 2);
              document.getElementById("capability_modules").textContent = JSON.stringify(data.groups.capability_modules, null, 2);
              document.getElementById("system").textContent = JSON.stringify(data.groups.system, null, 2);
              document.getElementById("state").textContent = JSON.stringify(data, null, 2);
            });
        </script>
      </body>
    </html>
    """


@router.get("/api/command/navigation")
async def navigation_api() -> dict[str, Any]:
    return build_navigation_payload()


@router.get("/command/navigation", response_class=HTMLResponse)
async def navigation_page() -> HTMLResponse:
    return HTMLResponse(content=render_navigation_html())
