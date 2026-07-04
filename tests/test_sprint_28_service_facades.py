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


def test_sprint_28_live_routes_still_work():
    for path in LIVE_PATHS:
        response = client.get(path)
        assert response.status_code == 200, path


def test_sprint_28_service_facades_exist():
    assert callable(records_service.get_records_state)
    assert callable(records_service.archive_record)
    assert callable(records_service.delete_record)
    assert callable(records_service.get_records_page)
    assert callable(daily_driver_service.get_daily_driver_state)
    assert callable(daily_driver_service.get_daily_driver_page)


def test_sprint_28_routes_call_service_facades_not_adapter_directly():
    records_text = Path("backend/routes/records.py").read_text()
    daily_text = Path("backend/routes/daily_driver.py").read_text()

    assert "backend.services.records_service" in records_text
    assert "backend.services.daily_driver_service" in daily_text
    assert "legacy_route_adapter" not in records_text
    assert "legacy_route_adapter" not in daily_text
    assert "call_main_handler" not in records_text
    assert "call_main_handler" not in daily_text


def test_sprint_28_service_facades_still_use_adapter_temporarily():
    records_service_text = Path("backend/services/records_service.py").read_text()
    daily_service_text = Path("backend/services/daily_driver_service.py").read_text()

    assert "call_main_handler" in records_service_text
    assert "call_main_handler" in daily_service_text
    assert "sprint16_record_management_state" in records_service_text
    assert "sprint15_daily_driver_state" in daily_service_text


def test_sprint_28_future_import_first():
    for path in [
        Path("backend/routes/records.py"),
        Path("backend/routes/daily_driver.py"),
        Path("backend/services/records_service.py"),
        Path("backend/services/daily_driver_service.py"),
    ]:
        first_non_empty = next(line for line in path.read_text().splitlines() if line.strip())
        assert first_non_empty == "from __future__ import annotations"


def test_sprint_28_docs_exist():
    assert Path("SPRINT_28_EXTRACT_RECORDS_DAILY_DRIVER_DATA_SERVICES.md").exists()
    assert Path("docs/SPRINT_28_SERVICE_FACADE_NOTES.md").exists()
    assert Path("backend/services/records_service.py").exists()
    assert Path("backend/services/daily_driver_service.py").exists()
