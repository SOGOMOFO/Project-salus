from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def setup_function():
    client.post("/mission-registry/reset")


def test_command_center_framework_loads():
    response = client.get("/command-center/framework")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Project Salus Command Center Orchestrator V1"
    assert "decision_firewall" in data["modules"]
    assert "dashboard" in data["outputs"]


def test_command_dashboard_generates_default_view():
    response = client.post("/command-center/dashboard", json={})
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "command_center_orchestrator_v1"
    assert data["command_readiness"]["overall_readiness_score"] <= 100
    assert data["command_readiness"]["readiness_level"] in ["green", "amber", "red"]
    assert data["priority_stack"]
    assert data["first_action"]


def test_command_dashboard_detects_blocked_mission():
    mission_payload = {
        "title": "Blocked AI Governance Mission",
        "objective": "Deploy a high-risk AI tool after controls are implemented.",
        "owner": "Kyle",
        "status": "blocked",
        "deadline": "2026-07-10",
        "strategic_fit": 8,
        "roi": 8,
        "urgency": 7,
        "risk": 8,
        "difficulty": 6,
        "opportunity_cost": 4,
        "success_criteria": ["Audit logging enabled", "Kill switch enabled"],
        "blockers": ["No kill switch"],
        "next_actions": ["Implement kill switch"],
    }

    client.post("/mission-registry/create", json=mission_payload)

    response = client.post("/command-center/dashboard", json={})
    assert response.status_code == 200

    data = response.json()
    assert data["mission_snapshot"]["status_counts"]["blocked"] == 1
    assert "Blocked missions require command attention." in data["risk_register"]["risk_flags"]
    assert data["priority_stack"][0]["priority"] == "Unblock mission"


def test_command_dashboard_prioritizes_ai_and_decision_reviews():
    payload = {
        "ai_tools_requiring_review": ["agent with Gmail access"],
        "open_decisions": ["whether to add another expert agent"],
        "wealth_flags": ["unassigned cash"],
        "echo_seven_targets": ["AI Governance & Cyber Readiness Assessment"],
    }

    response = client.post("/command-center/dashboard", json=payload)
    assert response.status_code == 200

    data = response.json()
    priorities = [item["priority"] for item in data["priority_stack"]]

    assert "Run AI governance review" in priorities
    assert "Run decision review" in priorities
    assert "Run Wealth OS review" in priorities
    assert "Advance Echo Seven" in priorities


def test_morning_brief_returns_action_lines():
    payload = {
        "commander_intent": "Execute the highest-leverage Salus mission.",
        "reported_risks": ["opportunity overload"],
        "constraints": ["limited focus time"],
    }

    response = client.post("/command-center/morning-brief", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["brief_name"] == "Project Salus Morning Command Brief"
    assert data["brief_lines"]
    assert "Commander intent:" in data["brief_lines"][0]
    assert data["top_priorities"]


def test_module_health_detects_empty_mission_memory():
    response = client.post("/command-center/module-health", json={})
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "command_center_module_health"
    assert "No registered missions found; execution memory is empty." in data["health_flags"]
