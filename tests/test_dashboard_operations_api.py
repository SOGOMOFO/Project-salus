from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_dashboard_missions_returns_mission_groups():
    response = client.get("/api/dashboard/missions")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "missions" in data
    assert "all" in data["missions"]
    assert "open" in data["missions"]
    assert "completed" in data["missions"]
    assert "blocked" in data["missions"]
    assert "counts" in data["missions"]


def test_dashboard_daily_returns_daily_data():
    response = client.get("/api/dashboard/daily")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "daily" in data
    assert "latest_sitrep" in data["daily"]
    assert "latest_aar" in data["daily"]
    assert "recent_sitreps" in data["daily"]
    assert "recent_aars" in data["daily"]
    assert "counts" in data["daily"]


def test_dashboard_health_returns_operating_health():
    response = client.get("/api/dashboard/health")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "health" in data
    assert "overall" in data["health"]
    assert "operating_status" in data["health"]
    assert "has_sitrep" in data["health"]
    assert "has_aar" in data["health"]
    assert "blocked_missions" in data["health"]
    assert "open_missions" in data["health"]
    assert "next_recommended_action" in data["health"]
