from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend import mission_control_service as service


client = TestClient(app)


def test_security_hardening_api_exists():
    response = client.get("/api/mission-control/security")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in {"ok", "warning", "blocked"}
    assert "auth_enabled" in data
    assert "required_security_headers" in data
    assert "recommended_action" in data


def test_security_hardening_service_checks_routes():
    state = service.get_security_hardening_state(app)
    assert state["route_status"]["checked"] is True
    assert "/api/mission-control/security" in state["route_status"]["present"]


def test_security_headers_present_on_security_api():
    response = client.get("/api/mission-control/security")
    assert response.headers.get("x-content-type-options") == "nosniff"
    assert response.headers.get("x-frame-options") == "DENY"
    assert response.headers.get("referrer-policy") == "no-referrer"
    assert "geolocation=()" in response.headers.get("permissions-policy", "")
    assert response.headers.get("cache-control") == "no-store"


def test_security_document_exists():
    text = Path("PROJECT_SALUS_SECURITY.md").read_text()
    assert "Project Salus Security Hardening" in text
    assert "External action firewall" in text
    assert "Production Warning" in text


def test_security_check_script_exists():
    assert Path("scripts/security_check.py").exists()
