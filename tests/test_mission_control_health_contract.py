from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_route_inventory_api():
    response = client.get("/api/mission-control/routes")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["routes"], list)
    assert any(route["path"] == "/mission-control/v1" for route in data["routes"])
    assert any(route["path"] == "/api/mission-control/agent/state" for route in data["routes"])


def test_mission_control_contract_api():
    response = client.get("/api/mission-control/contract")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["missing_paths"] == []
    assert data["counts"]["mission_control_routes"] >= 10
    assert data["counts"]["mission_control_api_routes"] >= 5


def test_mission_control_health_api():
    response = client.get("/api/mission-control/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] in {"ok", "degraded"}
    assert data["posture"] in {"healthy", "degraded", "attention_required"}
    assert "checks" in data
    assert "contract" in data
    assert "mission_control_readiness" in data
    assert "agent_counts" in data
    assert "risk" in data


def test_mission_control_v1_contains_system_health_panel():
    response = client.get("/mission-control/v1")
    assert response.status_code == 200

    assert "System Health" in response.text
    assert "Health JSON" in response.text
    assert "/api/mission-control/health" in response.text
    assert "/api/mission-control/contract" in response.text
    assert "/api/mission-control/routes" in response.text
