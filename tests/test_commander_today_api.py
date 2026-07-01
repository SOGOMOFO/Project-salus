from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_commander_today_endpoint_returns_daily_command_view():
    response = client.get("/api/commander/today")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "commander_today" in data

    command_view = data["commander_today"]

    assert command_view["operating_status"] == "active"
    assert "latest_sitrep" in command_view
    assert "latest_aar" in command_view
    assert "open_missions" in command_view
    assert "blocked_missions" in command_view
    assert "next_recommended_action" in command_view
    assert isinstance(command_view["open_missions"], list)
    assert isinstance(command_view["blocked_missions"], list)
