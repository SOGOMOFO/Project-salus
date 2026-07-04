from __future__ import annotations

from typing import Any, Callable

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["command-records"])

CountProvider = Callable[[str], int]
ArchiveProvider = Callable[[], int]


RECORDS_ROUTE_MANIFEST = {
    "api": "/api/command/records",
    "archive_api": "/api/command/records/archive",
    "delete_api": "/api/command/records/delete",
    "page": "/command/records",
    "module": "record_management_controls",
    "delete_confirmation_phrase": "DELETE_PROJECT_SALUS_RECORD",
}


RECORD_GROUPS = {
    "daily_operations": [
        "_sprint01_missions",
        "_sprint01_daily_briefs",
        "_sprint04_aars",
    ],
    "schoolhouse": [
        "_schoolhouse_courses",
        "_schoolhouse_study_sessions",
        "_schoolhouse_wrong_answer_reviews",
        "_schoolhouse_writing_tasks",
    ],
    "charisma": [
        "_charisma_self_assessments",
        "_charisma_conversation_aars",
    ],
}


def default_count_provider(_: str) -> int:
    return 0


def default_archive_provider() -> int:
    return 0


def build_records_payload(
    count_provider: CountProvider = default_count_provider,
    archive_provider: ArchiveProvider = default_archive_provider,
) -> dict[str, Any]:
    groups: dict[str, Any] = {}

    for group_name, stores in RECORD_GROUPS.items():
        store_rows = [
            {
                "store": store,
                "count": count_provider(store),
            }
            for store in stores
        ]

        groups[group_name] = {
            "stores": store_rows,
            "total": sum(row["count"] for row in store_rows),
        }

    return {
        "status": "ok",
        "module": "record_management_controls",
        "record_groups": groups,
        "archive_count": archive_provider(),
        "delete_confirmation_phrase": "DELETE_PROJECT_SALUS_RECORD",
        "available_actions": {
            "list": "/api/command/records",
            "archive": "/api/command/records/archive",
            "delete": "/api/command/records/delete",
            "page": "/command/records",
        },
        "safety_note": "Delete requires explicit confirmation phrase. Archive is preferred before delete.",
        "next_action": "Use /command/records to archive or delete bad demo records.",
    }


def build_archive_response(record_type: str | None = None, record_id: str | None = None) -> dict[str, Any]:
    if not record_type or not record_id:
        return {
            "status": "error",
            "module": "record_management_controls",
            "message": "record_type and record_id are required.",
        }

    return {
        "status": "ok",
        "module": "record_management_controls",
        "action": "archive",
        "record_type": record_type,
        "record_id": record_id,
        "message": "Archive request accepted by extracted records module.",
    }


def build_delete_response(
    record_type: str | None = None,
    record_id: str | None = None,
    confirmation: str | None = None,
) -> dict[str, Any]:
    if confirmation != "DELETE_PROJECT_SALUS_RECORD":
        return {
            "status": "error",
            "module": "record_management_controls",
            "message": "Delete requires confirmation phrase DELETE_PROJECT_SALUS_RECORD.",
        }

    if not record_type or not record_id:
        return {
            "status": "error",
            "module": "record_management_controls",
            "message": "record_type and record_id are required.",
        }

    return {
        "status": "ok",
        "module": "record_management_controls",
        "action": "delete",
        "record_type": record_type,
        "record_id": record_id,
        "message": "Delete request accepted by extracted records module.",
    }


def render_records_html() -> str:
    return """
    <!doctype html>
    <html>
      <head>
        <title>Project Salus — Record Management</title>
      </head>
      <body>
        <h1>Project Salus — Record Management</h1>
        <p>Archive or delete local demo records. Archive first when possible.</p>

        <h2>Navigation</h2>
        <a href="/command/dashboard-index">Dashboard Index</a>
        <a href="/command/readiness">Readiness</a>
        <a href="/command/navigation">Navigation</a>
        <a href="/command/workflows">Workflows</a>
        <a href="/command/daily-driver">Daily Driver</a>
        <a href="/command/ops">Ops</a>
        <a href="/command/review">Review</a>

        <h2>Record State</h2>
        <pre id="state">Loading records...</pre>

        <script>
          fetch("/api/command/records")
            .then(response => response.json())
            .then(data => {
              document.getElementById("state").textContent = JSON.stringify(data, null, 2);
            });
        </script>
      </body>
    </html>
    """

from backend.services.records_service import archive_record, delete_record, get_records_page, get_records_state

@router.get("/api/command/records")
async def sprint26_records_sprint16_record_management_state_bridge() -> Any:
    return await get_records_state()


@router.post("/api/command/records/archive")
async def sprint26_records_sprint16_archive_record_bridge(request: Request) -> Any:
    return await archive_record(request)


@router.post("/api/command/records/delete")
async def sprint26_records_sprint16_delete_record_bridge(request: Request) -> Any:
    return await delete_record(request)


@router.get("/command/records", response_class=HTMLResponse)
async def sprint26_records_sprint16_record_management_page_bridge() -> Any:
    return await get_records_page()
