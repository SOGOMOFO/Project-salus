from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_echo_seven_assessment_framework_loads():
    response = client.get("/echo-seven/assessment/framework")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Echo Seven AI Governance & Cyber Readiness Assessment"
    assert "starter_snapshot" in data["packages"]
    assert "implementation_sprint" in data["packages"]


def test_high_risk_client_gets_implementation_sprint():
    payload = {
        "business_name": "Local Financial Firm",
        "industry": "financial_services",
        "employee_count": 12,
        "uses_ai_tools": True,
        "ai_tools": ["ChatGPT", "Claude"],
        "sensitive_data_types": ["pii", "financial"],
        "compliance_needs": ["privacy", "vendor_risk"],
        "business_impact_ai_failure": "high",
        "has_ai_policy": False,
        "has_cyber_policy": False,
        "mfa_enabled": False,
        "backups_enabled": False,
        "endpoint_security": False,
        "access_controls": False,
        "incident_response_plan": False,
        "audit_logging": False,
        "vendor_review_process": False,
        "staff_training": False,
    }

    response = client.post("/echo-seven/assessment/client-readiness", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["recommended_package"] == "implementation_sprint"
    assert data["readiness_level"] == "high_risk"
    assert "ai_acceptable_use_policy_missing" in data["gaps"]
    assert "sensitive_data_exposure_review_needed" in data["gaps"]


def test_moderate_client_gets_readiness_assessment():
    payload = {
        "business_name": "Local Contractor",
        "industry": "construction",
        "employee_count": 8,
        "uses_ai_tools": True,
        "ai_tools": ["ChatGPT"],
        "sensitive_data_types": ["pii"],
        "compliance_needs": [],
        "business_impact_ai_failure": "medium",
        "has_ai_policy": False,
        "has_cyber_policy": True,
        "mfa_enabled": True,
        "backups_enabled": True,
        "endpoint_security": True,
        "access_controls": True,
        "incident_response_plan": False,
        "audit_logging": False,
        "vendor_review_process": False,
        "staff_training": True,
    }

    response = client.post("/echo-seven/assessment/client-readiness", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["recommended_package"] == "readiness_assessment"
    assert data["readiness_score"] >= 35
    assert "acceptable_use_policy" in data["recommended_deliverables"]


def test_stronger_client_gets_starter_snapshot():
    payload = {
        "business_name": "Professional Services Firm",
        "industry": "consulting",
        "employee_count": 5,
        "uses_ai_tools": True,
        "ai_tools": ["ChatGPT"],
        "sensitive_data_types": [],
        "compliance_needs": [],
        "business_impact_ai_failure": "low",
        "has_ai_policy": True,
        "has_cyber_policy": True,
        "mfa_enabled": True,
        "backups_enabled": True,
        "endpoint_security": True,
        "access_controls": True,
        "incident_response_plan": True,
        "audit_logging": True,
        "vendor_review_process": True,
        "staff_training": True,
    }

    response = client.post("/echo-seven/assessment/client-readiness", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["recommended_package"] == "starter_snapshot"
    assert data["readiness_level"] == "strong"
