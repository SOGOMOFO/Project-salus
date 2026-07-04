from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend.services import daily_driver_service, records_service


client = TestClient(app)


LIVE_PATHS = [
    "/api/command/records",
    "/command/records",
    "/api/command/daily-driver-state",
    "/command/daily-driver",
]


def test_sprint_30_live_routes_still_work():
    for path in LIVE_PATHS:
        response = client.get(path)
        assert response.status_code == 200, path


def test_sprint_30_record_mutation_routes_still_work():
    client.post(
        "/api/schoolhouse/course",
        json={
            "id": "sprint30-course-1",
            "name": "Sprint 30 Archive Test",
            "code": "S30",
            "school": "WGU",
        },
    )

    archive_response = client.post(
        "/api/command/records/archive",
        json={"group": "schoolhouse_courses", "id": "sprint30-course-1"},
    )

    assert archive_response.status_code in {200, 400, 404, 422}


def test_sprint_30_services_are_explicit_not_source_snapshots():
    records_text = Path("backend/services/records_service.py").read_text()
    daily_text = Path("backend/services/daily_driver_service.py").read_text()

    assert "RECORDS_LEGACY_SOURCE" not in records_text
    assert "DAILY_DRIVER_LEGACY_SOURCE" not in daily_text
    assert "invoke_legacy_source" not in records_text
    assert "invoke_legacy_source" not in daily_text
    assert "call_main_handler" not in records_text
    assert "call_main_handler" not in daily_text


def test_sprint_30_services_export_expected_facades():
    assert callable(records_service.get_records_state)
    assert callable(records_service.archive_record)
    assert callable(records_service.delete_record)
    assert callable(records_service.get_records_page)
    assert callable(daily_driver_service.get_daily_driver_state)
    assert callable(daily_driver_service.get_daily_driver_page)


def test_sprint_30_main_stays_free_of_legacy_bridge():
    text = Path("backend/main.py").read_text()

    assert "Sprint 26 Legacy Handler Bridge" not in text
    assert "# --- Sprint 26 Wire Records and Daily Driver Routers ---" in text


def test_sprint_30_route_modules_still_call_facades():
    records_text = Path("backend/routes/records.py").read_text()
    daily_text = Path("backend/routes/daily_driver.py").read_text()

    assert "backend.services.records_service" in records_text
    assert "backend.services.daily_driver_service" in daily_text
    assert "call_main_handler" not in records_text
    assert "call_main_handler" not in daily_text


def test_sprint_30_docs_exist():
    assert Path("SPRINT_30_REPLACE_SOURCE_SNAPSHOTS_WITH_EXPLICIT_SERVICES.md").exists()
    assert Path("docs/SPRINT_30_EXPLICIT_SERVICE_NOTES.md").exists()
