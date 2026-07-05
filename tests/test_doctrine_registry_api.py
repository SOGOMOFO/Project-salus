from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def setup_function():
    client.post("/doctrine-registry/reset")


def test_doctrine_registry_framework_loads():
    response = client.get("/doctrine-registry/framework")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Project Salus Doctrine Registry & Learning Loop V1"
    assert "active" in data["statuses"]
    assert "ai_governance" in data["categories"]


def test_create_and_read_doctrine():
    payload = {
        "title": "No Unchecked AI Authority",
        "statement": "No powerful AI tool or agent receives unchecked authority.",
        "category": "ai_governance",
        "status": "active",
        "evidence_level": "strong_evidence",
        "source": "ai_governance_module",
        "rationale": "Autonomous tools require controls before deployment.",
        "triggers": ["ai_tool_deployment"],
        "rules": ["Require audit logging", "Require kill switch", "Require human approval"],
        "risks_if_ignored": ["Data exposure", "Unauthorized action"],
        "confidence_score": 9,
    }

    create_response = client.post("/doctrine-registry/create", json=payload)
    assert create_response.status_code == 200

    created = create_response.json()
    assert created["saved"] is True
    doctrine_id = created["doctrine"]["doctrine_id"]

    read_response = client.get(f"/doctrine-registry/{doctrine_id}")
    assert read_response.status_code == 200

    data = read_response.json()
    assert data["found"] is True
    assert data["doctrine"]["title"] == payload["title"]
    assert data["doctrine"]["status"] == "active"


def test_list_filters_active_ai_governance_doctrine():
    active_payload = {
        "title": "Active AI Doctrine",
        "statement": "AI tools require controls.",
        "category": "ai_governance",
        "status": "active",
        "evidence_level": "strong_evidence",
    }

    proposed_payload = {
        "title": "Proposed Wealth Doctrine",
        "statement": "Every dollar needs a mission.",
        "category": "wealth",
        "status": "proposed",
        "evidence_level": "expert_opinion",
    }

    client.post("/doctrine-registry/create", json=active_payload)
    client.post("/doctrine-registry/create", json=proposed_payload)

    response = client.get("/doctrine-registry/list?category=ai_governance&status=active")
    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 1
    assert data["doctrine"][0]["title"] == "Active AI Doctrine"


def test_update_doctrine_status():
    payload = {
        "title": "Proposed Rule",
        "statement": "Test doctrine should be reviewed.",
        "category": "general",
        "status": "proposed",
        "evidence_level": "expert_opinion",
    }

    created = client.post("/doctrine-registry/create", json=payload).json()
    doctrine_id = created["doctrine"]["doctrine_id"]

    update_payload = {
        "doctrine_id": doctrine_id,
        "status": "active",
        "review_note": "Approved after review.",
    }

    response = client.post("/doctrine-registry/update-status", json=update_payload)
    assert response.status_code == 200

    data = response.json()
    assert data["updated"] is True
    assert data["doctrine"]["status"] == "active"
    assert "Approved after review." in data["doctrine"]["review_notes"]


def test_create_lesson_with_doctrine_candidate():
    payload = {
        "title": "Paste Blocks Prevent Shell Errors",
        "lesson": "Typing file paths and Python snippets directly into zsh causes parse errors.",
        "source": "mission_aar",
        "category": "mission_execution",
        "mission_id": "mission_test123",
        "severity": "high",
        "recommended_doctrine_update": "Use full paste blocks and file redirection when writing code from terminal.",
        "action_items": ["Use cat > file blocks", "Run py_compile before pytest"],
    }

    response = client.post("/doctrine-registry/lesson", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["saved"] is True
    assert data["lesson"]["severity"] == "high"
    assert data["doctrine_candidate"]["statement"] == payload["recommended_doctrine_update"]

    lessons_response = client.get("/doctrine-registry/lessons?category=mission_execution")
    lessons = lessons_response.json()
    assert lessons["count"] == 1


def test_dashboard_surfaces_review_needed_and_weak_evidence():
    proposed_payload = {
        "title": "Weak Claim Doctrine",
        "statement": "Do not treat viral AI pattern claims as authority.",
        "category": "critical_thinking",
        "status": "proposed",
        "evidence_level": "ai_generated_pattern",
    }

    client.post("/doctrine-registry/create", json=proposed_payload)

    response = client.get("/doctrine-registry/dashboard")
    assert response.status_code == 200

    data = response.json()
    assert data["total_doctrine"] == 1
    assert data["status_counts"]["proposed"] == 1
    assert "Proposed or review-needed doctrine requires command review." in data["risk_flags"]
    assert "Some doctrine has weak evidence and should not be treated as authority." in data["risk_flags"]
