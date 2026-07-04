from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend.services.legacy_source_executor import invoke_legacy_source


client = TestClient(app)


LIVE_PATHS = [
    "/api/command/records",
    "/command/records",
    "/api/command/daily-driver-state",
    "/command/daily-driver",
]


def test_sprint_29_live_routes_still_work():
    for path in LIVE_PATHS:
        response = client.get(path)
        assert response.status_code == 200, path


def test_sprint_29_mutation_routes_still_available():
    archive_response = client.post(
        "/api/command/records/archive",
        json={"group": "schoolhouse_courses", "id": "missing-demo"},
    )
    delete_response = client.post(
        "/api/command/records/delete",
        json={
            "group": "charisma_self_assessments",
            "id": "missing-demo",
            "confirmation": "wrong",
        },
    )

    assert archive_response.status_code in {200, 400, 404, 422}
    assert delete_response.status_code in {200, 400, 404, 422}


def test_sprint_29_main_no_longer_contains_legacy_handler_bridge():
    text = Path("backend/main.py").read_text()

    assert "Sprint 26 Wire Records and Daily Driver Routers" in text
    assert "Sprint 26 Legacy Handler Bridge" not in text
    assert "sprint16_record_management_state" not in text
    assert "sprint15_daily_driver_state" not in text


def test_sprint_29_services_own_behavior_source_snapshots():
    records_text = Path("backend/services/records_service.py").read_text()
    daily_text = Path("backend/services/daily_driver_service.py").read_text()

    assert "RECORDS_LEGACY_SOURCE" in records_text
    assert "DAILY_DRIVER_LEGACY_SOURCE" in daily_text
    assert "sprint16_record_management_state" in records_text
    assert "sprint15_daily_driver_state" in daily_text
    assert "call_main_handler" not in records_text
    assert "call_main_handler" not in daily_text


def test_sprint_29_route_modules_call_service_facades():
    records_text = Path("backend/routes/records.py").read_text()
    daily_text = Path("backend/routes/daily_driver.py").read_text()

    assert "backend.services.records_service" in records_text
    assert "backend.services.daily_driver_service" in daily_text
    assert "call_main_handler" not in records_text
    assert "call_main_handler" not in daily_text


def test_sprint_29_legacy_source_executor_exists():
    assert callable(invoke_legacy_source)
    assert Path("backend/services/legacy_source_executor.py").exists()


def test_sprint_29_docs_exist():
    assert Path("SPRINT_29_MOVE_RECORDS_DAILY_DRIVER_BEHAVIOR_INTO_SERVICES.md").exists()
    assert Path("docs/SPRINT_29_BEHAVIOR_SERVICE_EXTRACTION_NOTES.md").exists()
