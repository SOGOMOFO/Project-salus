from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend.routes.daily_driver import (
    DAILY_DRIVER_ROUTE_MANIFEST,
    build_daily_driver_payload,
    render_daily_driver_html,
    router as daily_driver_router,
)
from backend.routes.records import (
    RECORDS_ROUTE_MANIFEST,
    build_archive_response,
    build_delete_response,
    build_records_payload,
    render_records_html,
    router as records_router,
)


client = TestClient(app)


LIVE_GET_PATHS = [
    "/api/command/records",
    "/command/records",
    "/api/command/daily-driver-state",
    "/command/daily-driver",
]


def test_sprint_25_live_get_routes_still_work():
    for path in LIVE_GET_PATHS:
        response = client.get(path)
        assert response.status_code == 200, path


def test_sprint_25_live_record_mutation_routes_still_exist():
    archive_response = client.post(
        "/api/command/records/archive",
        json={"record_type": "missions", "record_id": "demo"},
    )
    delete_response = client.post(
        "/api/command/records/delete",
        json={
            "record_type": "missions",
            "record_id": "demo",
            "confirmation": "WRONG",
        },
    )

    assert archive_response.status_code in {200, 400, 404, 422}
    assert delete_response.status_code in {200, 400, 404, 422}


def test_sprint_25_records_module_payload_shape():
    payload = build_records_payload(lambda name: 1, lambda: 2)

    assert RECORDS_ROUTE_MANIFEST["api"] == "/api/command/records"
    assert RECORDS_ROUTE_MANIFEST["page"] == "/command/records"
    assert RECORDS_ROUTE_MANIFEST["delete_confirmation_phrase"] == "DELETE_PROJECT_SALUS_RECORD"
    assert payload["status"] == "ok"
    assert payload["module"] == "record_management_controls"
    assert payload["archive_count"] == 2
    assert "record_groups" in payload
    assert "Record Management" in render_records_html()
    assert len(records_router.routes) >= 4


def test_sprint_25_records_module_safety_responses():
    missing_archive = build_archive_response()
    bad_delete = build_delete_response(record_type="missions", record_id="1", confirmation="wrong")
    good_delete = build_delete_response(
        record_type="missions",
        record_id="1",
        confirmation="DELETE_PROJECT_SALUS_RECORD",
    )

    assert missing_archive["status"] == "error"
    assert bad_delete["status"] == "error"
    assert good_delete["status"] == "ok"
    assert good_delete["action"] == "delete"


def test_sprint_25_daily_driver_module_payload_shape():
    payload = build_daily_driver_payload(lambda name: 1)

    assert DAILY_DRIVER_ROUTE_MANIFEST["api"] == "/api/command/daily-driver-state"
    assert DAILY_DRIVER_ROUTE_MANIFEST["page"] == "/command/daily-driver"
    assert payload["status"] == "ok"
    assert payload["module"] == "daily_driver_polish"
    assert payload["primary_daily_page"] == "/command/workflows"
    assert payload["readiness_page"] == "/command/readiness"
    assert "morning_sequence" in payload
    assert "evening_sequence" in payload
    assert "Daily Driver" in render_daily_driver_html()
    assert len(daily_driver_router.routes) >= 2


def test_sprint_25_audit_detects_shadow_extracted_routes():
    import importlib.util

    spec = importlib.util.spec_from_file_location("salus_audit", "scripts/salus_audit.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    routes = module.collect_routes("backend/main.py")

    record_sources = [
        route.get("source_file", "")
        for route in routes
        if route.get("path") == "/api/command/records"
    ]

    daily_driver_sources = [
        route.get("source_file", "")
        for route in routes
        if route.get("path") == "/api/command/daily-driver-state"
    ]

    assert record_sources
    assert daily_driver_sources
    assert any("backend/routes" in source for source in record_sources)
    assert any("backend/routes" in source for source in daily_driver_sources)


def test_sprint_25_docs_exist():
    assert Path("SPRINT_25_EXTRACT_RECORDS_AND_DAILY_DRIVER_ROUTES.md").exists()
    assert Path("docs/SPRINT_25_RECORDS_DAILY_DRIVER_EXTRACTION_NOTES.md").exists()
    assert Path("backend/routes/records.py").exists()
    assert Path("backend/routes/daily_driver.py").exists()
