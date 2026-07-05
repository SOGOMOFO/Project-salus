from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def setup_function():
    client.post("/mission-registry/reset")
    client.post("/doctrine-registry/reset")
    client.post("/curiosity-parking-lot/reset")
    client.post("/workflow-orchestrator/reset")


def test_operator_console_framework_loads():
    response = client.get("/operator-console/framework")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Project Salus Operator Console V1"
    assert data["tracked_modules"] >= 10
    assert "overview" in data["outputs"]


def test_operator_overview_returns_unified_picture():
    response = client.post(
        "/operator-console/overview",
        json={"commander_intent": "Build faster without losing control."},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "operator_console_overview_v1"
    assert data["commander_intent"] == "Build faster without losing control."
    assert data["readiness"]["score"] <= 100
    assert "modules" in data
    assert "missions" in data
    assert "risk_flags" in data
    assert data["next_action"]


def test_operator_console_detects_blocked_mission():
    mission_payload = {
        "title": "Blocked Operator Test Mission",
        "objective": "Confirm console detects blocked missions.",
        "owner": "Kyle",
        "status": "blocked",
        "strategic_fit": 8,
        "roi": 8,
        "urgency": 7,
        "risk": 5,
        "difficulty": 5,
        "opportunity_cost": 3,
        "success_criteria": ["Console risk flag appears"],
        "blockers": ["Test blocker"],
    }

    client.post("/mission-registry/create", json=mission_payload)

    response = client.post("/operator-console/overview", json={})
    assert response.status_code == 200

    data = response.json()
    assert data["missions"]["status_counts"]["blocked"] == 1
    assert "Blocked missions require command attention." in data["risk_flags"]
    assert "Unblock mission" in data["next_action"]


def test_action_queue_returns_prioritized_actions():
    client.post(
        "/curiosity-parking-lot/park",
        json={
            "title": "Promotion Candidate",
            "summary": "High-value parked idea.",
            "topics": ["business"],
            "strategic_fit": 10,
            "evidence_strength": 9,
            "actionability": 9,
            "roi": 9,
            "urgency": 8,
            "risk": 2,
            "opportunity_cost": 2,
        },
    )

    response = client.get("/operator-console/action-queue")
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "operator_console_action_queue_v1"
    assert data["count"] >= 1
    assert data["actions"]
    assert data["next_action"]


def test_module_cards_include_framework_endpoints():
    response = client.get("/operator-console/modules")
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "operator_console_module_cards_v1"
    assert data["count"] >= 10
    assert any(card["key"] == "command_center" for card in data["cards"])
    assert all("framework_endpoint" in card for card in data["cards"])


def test_health_check_returns_score_and_level():
    response = client.get("/operator-console/health")
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "operator_console_health_check_v1"
    assert data["health_score"] <= 100
    assert data["health_level"] in ["green", "amber", "red"]
    assert data["next_action"]


def test_smoke_targets_include_operator_console():
    response = client.get("/operator-console/smoke-targets")
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "operator_console_smoke_targets_v1"
    assert "/operator-console/framework" in data["endpoints"]
    assert "pytest -q" in data["commands"]
