from fastapi.testclient import TestClient

from backend.main import app
from backend.routes.dashboard_index import (
    DASHBOARD_INDEX_ROUTE_MANIFEST,
    build_dashboard_index_payload,
    render_dashboard_index_html,
    router as dashboard_index_router,
)
from backend.routes.readiness import (
    READINESS_ROUTE_MANIFEST,
    build_readiness_payload,
    render_readiness_html,
    router as readiness_router,
)


client = TestClient(app)


def test_sprint_22_dashboard_index_module_exists():
    payload = build_dashboard_index_payload(lambda name: 1)

    assert DASHBOARD_INDEX_ROUTE_MANIFEST["api"] == "/api/command/dashboard-index"
    assert DASHBOARD_INDEX_ROUTE_MANIFEST["page"] == "/command/dashboard-index"
    assert payload["status"] == "ok"
    assert payload["module"] == "dashboard_index_final_local_mvp"
    assert payload["local_mvp_status"] == "complete"
    assert payload["data_counts"]["missions"] == 1
    assert "Dashboard Index" in render_dashboard_index_html()
    assert len(dashboard_index_router.routes) >= 2


def test_sprint_22_readiness_module_exists():
    payload = build_readiness_payload(lambda name: 1, lambda: 0)

    assert READINESS_ROUTE_MANIFEST["api"] == "/api/command/readiness"
    assert READINESS_ROUTE_MANIFEST["page"] == "/command/readiness"
    assert payload["status"] == "ok"
    assert payload["module"] == "system_status_readiness_scoring"
    assert payload["max_score"] == 100
    assert "components" in payload
    assert "Project Salus" in render_readiness_html()
    assert len(readiness_router.routes) >= 2


def test_sprint_22_existing_dashboard_routes_still_work():
    api_response = client.get("/api/command/dashboard-index")
    page_response = client.get("/command/dashboard-index")

    assert api_response.status_code == 200
    assert page_response.status_code == 200
    assert api_response.json()["module"] == "dashboard_index_final_local_mvp"


def test_sprint_22_existing_readiness_routes_still_work():
    api_response = client.get("/api/command/readiness")
    page_response = client.get("/command/readiness")

    assert api_response.status_code == 200
    assert page_response.status_code == 200
    assert api_response.json()["module"] == "system_status_readiness_scoring"


def test_sprint_22_extraction_docs_exist():
    from pathlib import Path

    assert Path("SPRINT_22_EXTRACT_DASHBOARD_INDEX_AND_READINESS_ROUTES.md").exists()
    assert Path("docs/SPRINT_22_ROUTE_EXTRACTION_NOTES.md").exists()
    assert Path("backend/routes/__init__.py").exists()
    assert Path("backend/routes/dashboard_index.py").exists()
    assert Path("backend/routes/readiness.py").exists()
