from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter
from fastapi.responses import HTMLResponse


router = APIRouter(tags=["command-readiness"])

CountProvider = Callable[[str], int]
ArchivedProvider = Callable[[], int]


READINESS_ROUTE_MANIFEST = {
    "api": "/api/command/readiness",
    "page": "/command/readiness",
    "module": "system_status_readiness_scoring",
}


def default_count_provider(_: str) -> int:
    return 0


def default_archived_provider() -> int:
    return 0


def readiness_level(score: int) -> str:
    if score >= 85:
        return "green"
    if score >= 65:
        return "amber"
    if score >= 40:
        return "red"
    return "critical"


def component(status: str, score: int, summary: str, recommendations: list[str]) -> dict[str, Any]:
    return {
        "status": status,
        "score": score,
        "summary": summary,
        "recommendations": recommendations,
    }


def build_readiness_payload(
    count_provider: CountProvider = default_count_provider,
    archived_provider: ArchivedProvider = default_archived_provider,
) -> dict[str, Any]:
    counts = {
        "missions": count_provider("_sprint01_missions"),
        "daily_briefs": count_provider("_sprint01_daily_briefs"),
        "aars": count_provider("_sprint04_aars"),
        "schoolhouse_courses": count_provider("_schoolhouse_courses"),
        "schoolhouse_study_sessions": count_provider("_schoolhouse_study_sessions"),
        "schoolhouse_wrong_answer_reviews": count_provider("_schoolhouse_wrong_answer_reviews"),
        "schoolhouse_writing_tasks": count_provider("_schoolhouse_writing_tasks"),
        "charisma_self_assessments": count_provider("_charisma_self_assessments"),
        "charisma_conversation_aars": count_provider("_charisma_conversation_aars"),
        "archived_records": archived_provider(),
    }

    daily_score = 0
    daily_recommendations: list[str] = []

    if counts["daily_briefs"] > 0:
        daily_score += 7
    else:
        daily_recommendations.append("Create a daily brief from /command/ops.")

    if counts["missions"] > 0:
        daily_score += 7
    else:
        daily_recommendations.append("Create at least one active mission.")

    if counts["aars"] > 0:
        daily_score += 6
    else:
        daily_recommendations.append("Close the day with one AAR.")

    schoolhouse_score = 0
    schoolhouse_recommendations: list[str] = []

    if counts["schoolhouse_courses"] > 0:
        schoolhouse_score += 10
    else:
        schoolhouse_recommendations.append("Add your current WGU course to Schoolhouse.")

    if counts["schoolhouse_study_sessions"] > 0:
        schoolhouse_score += 10
    else:
        schoolhouse_recommendations.append("Log one focused study session.")

    charisma_score = 0
    charisma_recommendations: list[str] = []

    if counts["charisma_self_assessments"] > 0:
        charisma_score += 10
    else:
        charisma_recommendations.append("Complete one charisma self-assessment.")

    if counts["charisma_conversation_aars"] > 0:
        charisma_score += 10
    else:
        charisma_recommendations.append("Log one important conversation AAR.")

    total_records = sum(value for key, value in counts.items() if key != "archived_records")

    hygiene_score = 20
    hygiene_recommendations: list[str] = []

    if counts["archived_records"] > 10:
        hygiene_score -= 5
        hygiene_recommendations.append("Review archived records and delete demo/test records if needed.")

    if total_records > 50:
        hygiene_score -= 5
        hygiene_recommendations.append("Review records for clutter from /command/records.")

    if not hygiene_recommendations:
        hygiene_recommendations.append("Data hygiene is acceptable.")

    system_score = 20

    components = {
        "system": component(
            "ok",
            system_score,
            "Local Project Salus app is responding.",
            [
                "Use /command/navigation for page access.",
                "Use /command/workflows as the primary daily operating guide.",
            ],
        ),
        "daily_operations": component(
            readiness_level(daily_score * 5),
            daily_score,
            "Daily loop readiness based on briefs, missions, and AARs.",
            daily_recommendations or ["Daily operations data exists."],
        ),
        "schoolhouse": component(
            readiness_level(schoolhouse_score * 5),
            schoolhouse_score,
            "Schoolhouse readiness based on course and study-session activity.",
            schoolhouse_recommendations or ["Schoolhouse activity exists."],
        ),
        "charisma": component(
            readiness_level(charisma_score * 5),
            charisma_score,
            "Charisma readiness based on self-assessment and conversation AAR activity.",
            charisma_recommendations or ["Charisma training activity exists."],
        ),
        "data_hygiene": component(
            readiness_level(hygiene_score * 5),
            hygiene_score,
            "Data hygiene based on total records and archived records.",
            hygiene_recommendations,
        ),
    }

    total_score = system_score + daily_score + schoolhouse_score + charisma_score + hygiene_score

    top_recommendations: list[str] = []
    for value in components.values():
        top_recommendations.extend(value["recommendations"])

    return {
        "status": "ok",
        "module": "system_status_readiness_scoring",
        "score": total_score,
        "max_score": 100,
        "readiness_level": readiness_level(total_score),
        "counts": counts,
        "components": components,
        "top_recommendations": top_recommendations[:8],
        "primary_pages": {
            "readiness": "/command/readiness",
            "navigation": "/command/navigation",
            "workflows": "/command/workflows",
            "daily_driver": "/command/daily-driver",
            "ops": "/command/ops",
            "review": "/command/review",
            "records": "/command/records",
        },
        "next_action": "Open /command/workflows and run the morning or evening checklist.",
    }



def render_readiness_html() -> str:
    return """
    <!doctype html>
    <html>
      <head>
        <title>Project Salus — Readiness</title>
      </head>
      <body>
        <h1>Project Salus — Readiness</h1>
        <p>Fast status view for the system, daily loop, Schoolhouse, Charisma, and data hygiene.</p>

        <h2>Navigation</h2>
        <a href="/command/workflows">Workflows</a>
        <a href="/command/navigation">Navigation Hub</a>
        <a href="/command/daily-driver">Daily Driver</a>
        <a href="/command/ops">Ops</a>
        <a href="/command/review">Review</a>
        <a href="/command/records">Records</a>

        <h2>Overall Readiness</h2>
        <pre id="summary">Loading readiness...</pre>

        <h2>System</h2>
        <pre id="system">Loading system...</pre>

        <h2>Daily Operations</h2>
        <pre id="daily_operations">Loading daily operations...</pre>

        <h2>Schoolhouse</h2>
        <pre id="schoolhouse">Loading Schoolhouse...</pre>

        <h2>Charisma</h2>
        <pre id="charisma">Loading Charisma...</pre>

        <h2>Data Hygiene</h2>
        <pre id="data_hygiene">Loading data hygiene...</pre>

        <h2>Full Readiness State</h2>
        <pre id="state">Loading state...</pre>

        <script>
          fetch("/api/command/readiness")
            .then(response => response.json())
            .then(data => {
              document.getElementById("summary").textContent = JSON.stringify({
                score: data.score,
                max_score: data.max_score,
                readiness_level: data.readiness_level,
                next_action: data.next_action,
                top_recommendations: data.top_recommendations
              }, null, 2);

              document.getElementById("system").textContent = JSON.stringify(data.components.system, null, 2);
              document.getElementById("daily_operations").textContent = JSON.stringify(data.components.daily_operations, null, 2);
              document.getElementById("schoolhouse").textContent = JSON.stringify(data.components.schoolhouse, null, 2);
              document.getElementById("charisma").textContent = JSON.stringify(data.components.charisma, null, 2);
              document.getElementById("data_hygiene").textContent = JSON.stringify(data.components.data_hygiene, null, 2);
              document.getElementById("state").textContent = JSON.stringify(data, null, 2);
            });
        </script>
      </body>
    </html>
    """

@router.get("/api/command/readiness")
async def readiness_api() -> dict[str, Any]:
    return build_readiness_payload()


@router.get("/command/readiness", response_class=HTMLResponse)
async def readiness_page() -> HTMLResponse:
    return HTMLResponse(content=render_readiness_html())
