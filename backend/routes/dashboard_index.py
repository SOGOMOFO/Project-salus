from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(tags=["command-dashboard-index"])

CountProvider = Callable[[str], int]


def default_count_provider(_: str) -> int:
    return 0


DASHBOARD_INDEX_ROUTE_MANIFEST = {
    "api": "/api/command/dashboard-index",
    "page": "/command/dashboard-index",
    "module": "dashboard_index_final_local_mvp",
}


def capability(name: str, status: str, description: str, pages: list[str], apis: list[str]) -> dict[str, Any]:
    return {
        "name": name,
        "status": status,
        "description": description,
        "pages": pages,
        "apis": apis,
    }


def build_dashboard_index_payload(count_provider: CountProvider = default_count_provider) -> dict[str, Any]:
    capabilities = [
        capability(
            "Core Command Loop",
            "complete",
            "Daily brief, missions, AAR logging, and judgment support foundation.",
            ["/command/daily"],
            ["/api/daily-brief", "/missions", "/api/aar", "/api/judgment"],
        ),
        capability(
            "Data Hygiene and Reset Controls",
            "complete",
            "Local development reset controls and persistent data cleanup support.",
            [],
            ["/api/dev/reset"],
        ),
        capability(
            "Schoolhouse Learning Coach",
            "complete",
            "Learning coach for courses, study sessions, quiz mode, and writing tasks.",
            ["/command/ops", "/command/review"],
            [
                "/api/schoolhouse/status",
                "/api/schoolhouse/course",
                "/api/schoolhouse/courses",
                "/api/schoolhouse/study-session",
                "/api/schoolhouse/daily-brief",
                "/api/schoolhouse/quiz",
                "/api/schoolhouse/wrong-answer-review",
                "/api/schoolhouse/writing-task",
            ],
        ),
        capability(
            "Charisma and Communication Skill",
            "complete",
            "Ethical communication, listening, presence, and conversation AAR capability.",
            ["/command/ops", "/command/review"],
            [
                "/api/skills/charisma",
                "/api/skills/charisma/self-assessment",
                "/api/skills/charisma/daily-drill",
                "/api/skills/charisma/conversation-aar",
            ],
        ),
        capability(
            "Operational Dashboard Controls",
            "complete",
            "Browser forms for daily brief, missions, Schoolhouse, and Charisma records.",
            ["/command/ops"],
            ["/api/command/integrated-state"],
        ),
        capability(
            "Operational Review and History",
            "complete",
            "Browser review of stored missions, briefs, AARs, Schoolhouse records, and Charisma records.",
            ["/command/review"],
            ["/api/command/review-state"],
        ),
        capability(
            "Command Launcher and Navigation",
            "complete",
            "Command home, navigation hub, local launch scripts, and health endpoint.",
            ["/command/home", "/command/navigation"],
            ["/api/command/health", "/api/command/navigation"],
        ),
        capability(
            "Daily Driver and Workflows",
            "complete",
            "Daily driver page and guided morning/evening workflow automation.",
            ["/command/daily-driver", "/command/workflows"],
            [
                "/api/command/daily-driver-state",
                "/api/workflows/morning",
                "/api/workflows/evening",
                "/api/workflows/today",
            ],
        ),
        capability(
            "Record Management",
            "complete",
            "Archive and delete controls for local records.",
            ["/command/records"],
            ["/api/command/records", "/api/command/records/archive", "/api/command/records/delete"],
        ),
        capability(
            "System Readiness",
            "complete",
            "Readiness scoring for system, daily operations, Schoolhouse, Charisma, and data hygiene.",
            ["/command/readiness"],
            ["/api/command/readiness"],
        ),
        capability(
            "Dashboard Index",
            "complete",
            "Final local MVP dashboard index and capability inventory.",
            ["/command/dashboard-index"],
            ["/api/command/dashboard-index"],
        ),
    ]

    primary_pages = {
        "dashboard_index": "/command/dashboard-index",
        "readiness": "/command/readiness",
        "navigation": "/command/navigation",
        "workflows": "/command/workflows",
        "daily_driver": "/command/daily-driver",
        "command_home": "/command/home",
        "ops": "/command/ops",
        "review": "/command/review",
        "records": "/command/records",
        "integrated": "/command/integrated",
        "daily": "/command/daily",
    }

    data_counts = {
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
        "module": "dashboard_index_final_local_mvp",
        "project": "Project Salus Mission Control",
        "local_mvp_status": "complete",
        "capability_count": len(capabilities),
        "capabilities": capabilities,
        "primary_pages": primary_pages,
        "local_scripts": {
            "start": "scripts/start_salus.sh",
            "stop": "scripts/stop_salus.sh",
        },
        "data_counts": data_counts,
        "recommended_start_page": "/command/dashboard-index",
        "recommended_daily_page": "/command/workflows",
        "recommended_status_page": "/command/readiness",
        "next_action": "Use /command/dashboard-index as the local MVP index and /command/workflows for daily execution.",
    }



def render_dashboard_index_html() -> str:
    return """
    <!doctype html>
    <html>
      <head>
        <title>Project Salus — Dashboard Index</title>
      </head>
      <body>
        <h1>Project Salus — Dashboard Index</h1>
        <p>Final local MVP capability inventory and page index.</p>

        <h2>Primary Launch Points</h2>
        <a href="/command/readiness">Readiness</a>
        <a href="/command/navigation">Navigation</a>
        <a href="/command/workflows">Daily Workflows</a>
        <a href="/command/daily-driver">Daily Driver</a>
        <a href="/command/ops">Ops</a>
        <a href="/command/review">Review</a>
        <a href="/command/records">Records</a>

        <h2>Local MVP Status</h2>
        <pre id="summary">Loading dashboard index...</pre>

        <h2>Capabilities</h2>
        <pre id="capabilities">Loading capabilities...</pre>

        <h2>Primary Pages</h2>
        <pre id="pages">Loading pages...</pre>

        <h2>Local Scripts</h2>
        <pre id="scripts">Loading scripts...</pre>

        <h2>Data Counts</h2>
        <pre id="counts">Loading counts...</pre>

        <h2>Full Dashboard Index State</h2>
        <pre id="state">Loading state...</pre>

        <script>
          fetch("/api/command/dashboard-index")
            .then(response => response.json())
            .then(data => {
              document.getElementById("summary").textContent = JSON.stringify({
                project: data.project,
                local_mvp_status: data.local_mvp_status,
                capability_count: data.capability_count,
                recommended_start_page: data.recommended_start_page,
                recommended_daily_page: data.recommended_daily_page,
                recommended_status_page: data.recommended_status_page,
                next_action: data.next_action
              }, null, 2);

              document.getElementById("capabilities").textContent = JSON.stringify(data.capabilities, null, 2);
              document.getElementById("pages").textContent = JSON.stringify(data.primary_pages, null, 2);
              document.getElementById("scripts").textContent = JSON.stringify(data.local_scripts, null, 2);
              document.getElementById("counts").textContent = JSON.stringify(data.data_counts, null, 2);
              document.getElementById("state").textContent = JSON.stringify(data, null, 2);
            });
        </script>
      </body>
    </html>
    """

@router.get("/api/command/dashboard-index")
async def dashboard_index_api() -> dict[str, Any]:
    return build_dashboard_index_payload()


@router.get("/command/dashboard-index", response_class=HTMLResponse)
async def dashboard_index_page() -> HTMLResponse:
    return HTMLResponse(content=render_dashboard_index_html())
