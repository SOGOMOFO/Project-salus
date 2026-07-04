from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend.services.legacy_route_adapter import call_main_handler


client = TestClient(app)


LIVE_PATHS = [
    "/api/command/records",
    "/command/records",
    "/api/command/daily-driver-state",
    "/command/daily-driver",
]


def test_sprint_27_live_routes_still_work():
    for path in LIVE_PATHS:
        response = client.get(path)
        assert response.status_code == 200, path


def test_sprint_27_central_adapter_exists():
    assert callable(call_main_handler)
    assert Path("backend/services/legacy_route_adapter.py").exists()


def test_sprint_27_route_modules_do_not_define_duplicate_bridge():
    records_text = Path("backend/routes/records.py").read_text()
    daily_driver_text = Path("backend/routes/daily_driver.py").read_text()

    assert "async def _call_legacy_handler" not in records_text
    assert "async def _call_legacy_handler" not in daily_driver_text
    assert ("call_main_handler" in records_text) or ("backend.services.records_service" in records_text)
    assert ("call_main_handler" in daily_driver_text) or ("backend.services.daily_driver_service" in daily_driver_text)


def test_sprint_27_route_modules_keep_future_import_first():
    for path in [Path("backend/routes/records.py"), Path("backend/routes/daily_driver.py")]:
        first_non_empty = next(line for line in path.read_text().splitlines() if line.strip())
        assert first_non_empty == "from __future__ import annotations"


def test_sprint_27_existing_mutation_routes_still_available():
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


def test_sprint_27_docs_exist():
    assert Path("SPRINT_27_REMOVE_RECORDS_DAILY_DRIVER_LEGACY_BRIDGE.md").exists()
    assert Path("docs/SPRINT_27_LEGACY_ROUTE_ADAPTER_NOTES.md").exists()
