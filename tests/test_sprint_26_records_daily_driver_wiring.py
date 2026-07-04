from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend.routes.daily_driver import DAILY_DRIVER_ROUTE_MANIFEST
from backend.routes.records import RECORDS_ROUTE_MANIFEST


client = TestClient(app)


LIVE_GET_PATHS = [
    "/api/command/records",
    "/command/records",
    "/api/command/daily-driver-state",
    "/command/daily-driver",
]


def test_sprint_26_live_get_routes_work_after_wiring():
    for path in LIVE_GET_PATHS:
        response = client.get(path)
        assert response.status_code == 200, path


def test_sprint_26_records_mutation_routes_remain_available():
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


def test_sprint_26_route_manifests_preserved():
    assert RECORDS_ROUTE_MANIFEST["api"] == "/api/command/records"
    assert RECORDS_ROUTE_MANIFEST["page"] == "/command/records"
    assert DAILY_DRIVER_ROUTE_MANIFEST["api"] == "/api/command/daily-driver-state"
    assert DAILY_DRIVER_ROUTE_MANIFEST["page"] == "/command/daily-driver"


def test_sprint_26_main_has_wiring_and_no_old_direct_blocks():
    text = Path("backend/main.py").read_text()

    assert "# --- Sprint 26 Wire Records and Daily Driver Routers ---" in text
    assert "# --- Sprint 15 Daily Driver Polish ---" not in text
    assert "# --- Sprint 16 Record Management Controls ---" not in text
    assert "Sprint 26 Legacy Handler Bridge" in text


def test_sprint_26_audit_detects_wired_route_sources():
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
    assert all("backend/routes" in source for source in record_sources)
    assert all("backend/routes" in source for source in daily_driver_sources)


def test_sprint_26_docs_exist():
    assert Path("SPRINT_26_WIRE_RECORDS_AND_DAILY_DRIVER_ROUTERS.md").exists()
    assert Path("docs/SPRINT_26_RECORDS_DAILY_DRIVER_WIRING_NOTES.md").exists()
