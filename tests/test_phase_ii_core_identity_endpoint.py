from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend.services.core_identity_service import (
    core_identity_bundle,
    core_identity_status,
    read_doctrine_file,
)


client = TestClient(app)


def test_core_identity_status_route():
    response = client.get("/api/core-identity/status")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["module"] == "core_identity"
    assert data["doctrine_count"] == 5
    assert "Human Judgment System" in data["identity"]


def test_core_identity_bundle_route():
    response = client.get("/api/core-identity")

    assert response.status_code == 200
    data = response.json()
    assert "doctrine" in data
    assert "constitution" in data["doctrine"]
    assert "Prime Directive" in data["doctrine"]["constitution"]["content"]


def test_core_identity_doctrine_plain_text_route():
    response = client.get("/api/core-identity/doctrine/decision_standard")

    assert response.status_code == 200
    assert "Salus Decision Standard" in response.text
    assert "Recommendation Values" in response.text


def test_core_identity_page_loads():
    response = client.get("/command/core-identity")

    assert response.status_code == 200
    assert "Project Salus" in response.text
    assert "Core Identity" in response.text


def test_core_identity_service_functions():
    status = core_identity_status()
    bundle = core_identity_bundle()
    constitution = read_doctrine_file("constitution")

    assert status["doctrine_count"] == 5
    assert "doctrine" in bundle
    assert constitution["exists"] is True
    assert "Project Salus Constitution" in constitution["content"]


def test_core_identity_docs_exist():
    assert Path("PHASE_II_CORE_IDENTITY_ENDPOINT.md").exists()
    assert Path("backend/services/core_identity_service.py").exists()
    assert Path("backend/routes/core_identity.py").exists()
