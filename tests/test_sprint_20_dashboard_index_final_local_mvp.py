
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_20_dashboard_index_endpoint():
    response = client.get("/api/command/dashboard-index")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["module"] == "dashboard_index_final_local_mvp"
    assert data["project"] == "Project Salus Mission Control"
    assert data["local_mvp_status"] == "complete"
    assert data["capability_count"] >= 10
    assert "capabilities" in data
    assert "primary_pages" in data
    assert data["primary_pages"]["dashboard_index"] == "/command/dashboard-index"
    assert data["recommended_daily_page"] == "/command/workflows"
    assert data["recommended_status_page"] == "/command/readiness"
    assert data["local_scripts"]["start"] == "scripts/start_salus.sh"


def test_sprint_20_dashboard_index_page_loads():
    response = client.get("/command/dashboard-index")

    assert response.status_code == 200
    assert "Project Salus — Dashboard Index" in response.text
    assert "Final local MVP capability inventory" in response.text
    assert "Readiness" in response.text
    assert "Daily Workflows" in response.text
    assert "Local MVP Status" in response.text
    assert "/api/command/dashboard-index" in response.text
