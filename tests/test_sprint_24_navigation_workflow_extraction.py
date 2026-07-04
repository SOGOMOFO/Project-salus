from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend.routes.navigation import (
    NAVIGATION_ROUTE_MANIFEST,
    build_navigation_payload,
    render_navigation_html,
)
from backend.routes.workflows import (
    WORKFLOWS_ROUTE_MANIFEST,
    build_evening_workflow,
    build_morning_workflow,
    build_today_workflows,
    render_workflows_html,
)


client = TestClient(app)


TARGET_PATHS = [
    "/api/command/navigation",
    "/command/navigation",
    "/api/workflows/morning",
    "/api/workflows/evening",
    "/api/workflows/today",
    "/command/workflows",
]


def test_sprint_24_live_routes_still_work():
    for path in TARGET_PATHS:
        response = client.get(path)
        assert response.status_code == 200, path


def test_sprint_24_navigation_module_payload():
    payload = build_navigation_payload()

    assert NAVIGATION_ROUTE_MANIFEST["api"] == "/api/command/navigation"
    assert NAVIGATION_ROUTE_MANIFEST["page"] == "/command/navigation"
    assert payload["status"] == "ok"
    assert payload["module"] == "navigation_unification_ux_cleanup"
    assert payload["primary_daily_page"] == "/command/workflows"
    assert payload["primary_pages"]["readiness"] == "/command/readiness"
    assert "Navigation Hub" in render_navigation_html()


def test_sprint_24_workflow_module_payloads():
    morning = build_morning_workflow(lambda name: 1)
    evening = build_evening_workflow(lambda name: 1)
    today = build_today_workflows(lambda name: 1)

    assert WORKFLOWS_ROUTE_MANIFEST["page"] == "/command/workflows"
    assert morning["status"] == "ok"
    assert morning["workflow"] == "morning"
    assert morning["first_action"] == "Open /command/daily-driver."
    assert evening["status"] == "ok"
    assert evening["workflow"] == "evening"
    assert evening["final_action"] == "Set tomorrow’s first next action."
    assert today["module"] == "daily_workflow_automation"
    assert "Daily Workflow Automation" in render_workflows_html()


def test_sprint_24_main_no_longer_contains_removed_sprint_blocks():
    text = Path("backend/main.py").read_text()

    assert "# --- Sprint 24 Extract Navigation and Workflow Routers ---" in text
    assert "# --- Sprint 17 Daily Workflow Automation ---" not in text
    assert "# --- Sprint 18 Navigation Unification and UX Cleanup ---" not in text


def test_sprint_24_audit_detects_extracted_routes():
    import importlib.util

    spec = importlib.util.spec_from_file_location("salus_audit", "scripts/salus_audit.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    routes = module.collect_routes("backend/main.py")
    by_path = {route["path"]: route for route in routes}

    assert "/api/command/navigation" in by_path
    assert "/api/workflows/morning" in by_path
    assert "/api/workflows/today" in by_path
    assert "backend/routes" in by_path["/api/command/navigation"]["source_file"]
    assert "backend/routes" in by_path["/api/workflows/today"]["source_file"]


def test_sprint_24_docs_exist():
    assert Path("SPRINT_24_EXTRACT_NAVIGATION_AND_WORKFLOW_ROUTES.md").exists()
    assert Path("docs/SPRINT_24_NAVIGATION_WORKFLOW_EXTRACTION_NOTES.md").exists()
    assert Path("backend/routes/navigation.py").exists()
    assert Path("backend/routes/workflows.py").exists()
