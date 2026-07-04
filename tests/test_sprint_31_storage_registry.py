from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend.services import storage_registry


client = TestClient(app)


LIVE_PATHS = [
    "/api/command/records",
    "/command/records",
    "/api/command/daily-driver-state",
    "/command/daily-driver",
]


def test_sprint_31_live_routes_still_work():
    for path in LIVE_PATHS:
        response = client.get(path)
        assert response.status_code == 200, path


def test_sprint_31_storage_registry_exists():
    assert callable(storage_registry.legacy_main_namespace)
    assert callable(storage_registry.sync_legacy_globals)
    assert callable(storage_registry.resolve_legacy_name)
    assert callable(storage_registry.legacy_store_count)
    assert callable(storage_registry.available_legacy_stores)


def test_sprint_31_storage_registry_can_list_store_candidates():
    stores = storage_registry.available_legacy_stores()

    assert isinstance(stores, list)
    assert any(name.startswith("_") for name in stores)


def test_sprint_31_services_use_storage_registry_not_direct_main_sync():
    records_text = Path("backend/services/records_service.py").read_text()
    daily_text = Path("backend/services/daily_driver_service.py").read_text()

    assert "backend.services.storage_registry" in records_text
    assert "backend.services.storage_registry" in daily_text
    assert "import backend.main as legacy_main" not in records_text
    assert "import backend.main as legacy_main" not in daily_text
    assert "vars(legacy_main)" not in records_text
    assert "vars(legacy_main)" not in daily_text


def test_sprint_31_services_remain_explicit():
    records_text = Path("backend/services/records_service.py").read_text()
    daily_text = Path("backend/services/daily_driver_service.py").read_text()

    assert "RECORDS_LEGACY_SOURCE" not in records_text
    assert "DAILY_DRIVER_LEGACY_SOURCE" not in daily_text
    assert "invoke_legacy_source" not in records_text
    assert "invoke_legacy_source" not in daily_text
    assert "call_main_handler" not in records_text
    assert "call_main_handler" not in daily_text


def test_sprint_31_route_modules_still_call_service_facades():
    records_text = Path("backend/routes/records.py").read_text()
    daily_text = Path("backend/routes/daily_driver.py").read_text()

    assert "backend.services.records_service" in records_text
    assert "backend.services.daily_driver_service" in daily_text
    assert "call_main_handler" not in records_text
    assert "call_main_handler" not in daily_text


def test_sprint_31_docs_exist():
    assert Path("SPRINT_31_EXTRACT_SHARED_STORAGE_AND_STORE_HELPERS.md").exists()
    assert Path("docs/SPRINT_31_STORAGE_REGISTRY_NOTES.md").exists()
    assert Path("backend/services/storage_registry.py").exists()
