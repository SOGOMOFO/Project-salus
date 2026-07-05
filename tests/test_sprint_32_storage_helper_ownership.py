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


def test_sprint_32_live_routes_still_work():
    for path in LIVE_PATHS:
        response = client.get(path)
        assert response.status_code == 200, path


def test_sprint_32_storage_registry_owns_core_helpers():
    assert callable(storage_registry.sync_service_globals)
    assert callable(storage_registry.get_store)
    assert callable(storage_registry.store_count)
    assert callable(storage_registry.store_counts)
    assert callable(storage_registry.normalize_record_mutation_payload)
    assert callable(storage_registry.storage_registry_status)


def test_sprint_32_payload_normalization_supports_old_and_new_keys():
    old_payload = {"record_type": "missions", "record_id": "demo"}
    new_payload = {"group": "missions", "id": "demo"}

    assert storage_registry.normalize_record_mutation_payload(old_payload)["group"] == "missions"
    assert storage_registry.normalize_record_mutation_payload(old_payload)["id"] == "demo"
    assert storage_registry.normalize_record_mutation_payload(new_payload)["group"] == "missions"
    assert storage_registry.normalize_record_mutation_payload(new_payload)["id"] == "demo"


def test_sprint_32_storage_registry_status_shape():
    status = storage_registry.storage_registry_status()

    assert "available_store_count" in status
    assert "available_stores" in status
    assert isinstance(status["available_stores"], list)


def test_sprint_32_records_service_uses_registry_helpers():
    text = Path("backend/services/records_service.py").read_text()

    assert "normalize_record_mutation_payload" in text
    assert "sync_service_globals" in text
    assert "import backend.main as legacy_main" not in text
    assert "vars(legacy_main)" not in text


def test_sprint_32_daily_driver_service_uses_registry_sync():
    text = Path("backend/services/daily_driver_service.py").read_text()

    assert "sync_service_globals" in text
    assert "import backend.main as legacy_main" not in text
    assert "vars(legacy_main)" not in text


def test_sprint_32_docs_exist():
    assert Path("SPRINT_32_MOVE_CORE_STORE_OWNERSHIP_TO_STORAGE_REGISTRY.md").exists()
    assert Path("docs/SPRINT_32_STORAGE_HELPER_OWNERSHIP_NOTES.md").exists()
