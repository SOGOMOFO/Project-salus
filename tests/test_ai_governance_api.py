from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_ai_governance_framework_loads():
    response = client.get("/ai-governance/framework")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Project Salus AI Governance Checklist"
    assert "audit_logging" in data["required_controls"]
    assert "kill_switch" in data["required_controls"]


def test_low_risk_assistive_tool_is_approved():
    payload = {
        "tool_name": "Study Helper",
        "purpose": "Help Kyle study cybersecurity concepts.",
        "data_types": ["public_notes"],
        "access_level": "read",
        "autonomy_level": "assistive",
        "external_connections": [],
        "business_impact": "low",
        "human_approval_required": True,
        "audit_logging": True,
        "kill_switch": True,
        "model_fallback": True,
        "output_verification": True,
    }

    response = client.post("/ai-governance/assess-tool", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["decision"] == "APPROVED"
    assert data["risk_level"] == "green"


def test_high_risk_autonomous_tool_is_blocked_without_controls():
    payload = {
        "tool_name": "Autonomous Business Agent",
        "purpose": "Send emails, change records, and make business decisions.",
        "data_types": ["pii", "financial", "credentials"],
        "access_level": "admin",
        "autonomy_level": "acts_autonomously",
        "external_connections": ["gmail", "calendar", "banking"],
        "business_impact": "high",
        "human_approval_required": False,
        "audit_logging": False,
        "kill_switch": False,
        "model_fallback": False,
        "output_verification": False,
    }

    response = client.post("/ai-governance/assess-tool", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["decision"] == "BLOCKED_UNTIL_REMEDIATED"
    assert data["risk_level"] == "red"
    assert "audit_logging" in data["missing_controls"]
    assert "kill_switch" in data["missing_controls"]
