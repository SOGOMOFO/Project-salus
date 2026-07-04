
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_18_navigation_endpoint():
    response = client.get("/api/command/navigation")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["module"] == "navigation_unification_ux_cleanup"
    assert data["primary_daily_page"] == "/command/workflows"
    assert data["primary_pages"]["workflows"] == "/command/workflows"
    assert data["primary_pages"]["records"] == "/command/records"
    assert "daily_operations" in data["groups"]
    assert "review_and_records" in data["groups"]
    assert "capability_modules" in data["groups"]


def test_sprint_18_navigation_page_loads():
    response = client.get("/command/navigation")

    assert response.status_code == 200
    assert "Navigation Hub" in response.text
    assert "Primary Daily Guide" in response.text
    assert "/command/workflows" in response.text
    assert "/command/daily-driver" in response.text
    assert "/command/ops" in response.text
    assert "/command/review" in response.text
    assert "/command/records" in response.text
