from collections import Counter
from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend.routes.dashboard_index import build_dashboard_index_payload
from backend.routes.readiness import build_readiness_payload


client = TestClient(app)


TARGET_PATHS = [
    "/api/command/dashboard-index",
    "/command/dashboard-index",
    "/api/command/readiness",
    "/command/readiness",
]


def test_sprint_23_live_routes_still_work():
    for path in TARGET_PATHS:
        response = client.get(path)
        assert response.status_code == 200, path


def test_sprint_23_dashboard_index_served_from_extracted_payload_shape():
    response = client.get("/api/command/dashboard-index")
    data = response.json()

    assert data["status"] == "ok"
    assert data["module"] == "dashboard_index_final_local_mvp"
    assert data["local_mvp_status"] == "complete"
    assert data["recommended_daily_page"] == "/command/workflows"

    module_payload = build_dashboard_index_payload(lambda name: 0)
    assert module_payload["module"] == data["module"]


def test_sprint_23_readiness_served_from_extracted_payload_shape():
    response = client.get("/api/command/readiness")
    data = response.json()

    assert data["status"] == "ok"
    assert data["module"] == "system_status_readiness_scoring"
    assert data["max_score"] == 100
    assert "components" in data

    module_payload = build_readiness_payload(lambda name: 0, lambda: 0)
    assert module_payload["module"] == data["module"]


def test_sprint_23_no_duplicate_live_routes_for_extracted_paths():
    for path in TARGET_PATHS:
        response = client.get(path)
        assert response.status_code == 200, path

def test_sprint_23_main_no_longer_contains_removed_sprint_blocks():
    text = Path("backend/main.py").read_text()

    assert "# --- Sprint 23 Wire Extracted Dashboard and Readiness Routers ---" in text
    assert "# --- Sprint 19 System Status and Readiness Scoring ---" not in text
    assert "# --- Sprint 20 Dashboard Index and Final Local MVP Checkpoint ---" not in text


def test_sprint_23_audit_detects_extracted_routes():
    import importlib.util

    spec = importlib.util.spec_from_file_location("salus_audit", "scripts/salus_audit.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    routes = module.collect_routes("backend/main.py")
    by_path = {route["path"]: route for route in routes}

    assert "/api/command/dashboard-index" in by_path
    assert "/api/command/readiness" in by_path
    assert "backend/routes" in by_path["/api/command/dashboard-index"]["source_file"]
    assert "backend/routes" in by_path["/api/command/readiness"]["source_file"]


def test_sprint_23_docs_exist():
    assert Path("SPRINT_23_WIRE_EXTRACTED_ROUTERS.md").exists()
    assert Path("docs/SPRINT_23_ROUTER_WIRING_NOTES.md").exists()
