from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_daily_brief_v2_framework_loads():
    response = client.get("/daily-brief-v2/framework")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Project Salus Daily Commander Brief V2"
    assert "mission" in data["readiness_areas"]
    assert "connect_to_decision_firewall" in data["required_logic"]


def test_daily_brief_generates_priority_stack():
    payload = {
        "date": "2026-07-05",
        "commander_intent": "Build Project Salus into a disciplined command operating system.",
        "top_objectives": [
            "Finish current Project Salus build block",
            "Keep WGU/cybersecurity path moving",
        ],
        "active_risks": ["opportunity overload"],
        "constraints": ["limited focus time"],
        "decisions_pending": ["whether to add another agent"],
        "ai_tools_requiring_review": ["autonomous business assistant"],
        "wealth_flags": ["unassigned cash"],
        "echo_seven_targets": ["AI Governance & Cyber Readiness Assessment"],
        "family_focus": ["weekly family AAR"],
        "health_focus": ["cardio restart"],
        "learning_focus": ["cybersecurity study block"],
    }

    response = client.post("/daily-brief-v2/generate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["brief_name"] == "Project Salus Daily Commander Brief"
    assert data["overall_readiness_score"] <= 100
    assert data["readiness_level"] in ["green", "amber", "red"]
    assert data["priority_stack"]
    assert "Pending decisions require Decision Firewall review." in data["risk_register"]["warnings"]


def test_daily_brief_defaults_when_empty():
    response = client.post("/daily-brief-v2/generate", json={})
    assert response.status_code == 200

    data = response.json()
    assert data["commander_intent"]
    assert data["priority_stack"][0]["priority"] == "Maintain Mission Readiness"
    assert data["next_action"] == "Execute the top scheduled mission and log an AAR."


def test_daily_brief_prioritizes_ai_governance_when_ai_tools_present():
    payload = {
        "ai_tools_requiring_review": ["agent with Gmail access"],
        "active_risks": [],
        "constraints": [],
    }

    response = client.post("/daily-brief-v2/generate", json=payload)
    assert response.status_code == 200

    data = response.json()
    priorities = [item["priority"] for item in data["priority_stack"]]
    assert "Run AI Governance Review" in priorities
    assert "AI tools require governance review before expanded use." in data["risk_register"]["warnings"]
