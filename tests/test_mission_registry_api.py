from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def setup_function():
    client.post("/mission-registry/reset")


def test_mission_registry_framework_loads():
    response = client.get("/mission-registry/framework")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Project Salus Mission Registry & Persistence V1"
    assert "active" in data["statuses"]
    assert "missions" in data["records"]


def test_create_and_read_registry_mission():
    payload = {
        "title": "Echo Seven Outreach Sprint",
        "objective": "Contact three warm leads for the AI Governance & Cyber Readiness Assessment.",
        "source": "mission_execution",
        "owner": "Kyle",
        "status": "planned",
        "deadline": "2026-07-06",
        "strategic_fit": 10,
        "roi": 9,
        "urgency": 8,
        "risk": 3,
        "difficulty": 4,
        "opportunity_cost": 2,
        "success_criteria": ["Three messages sent", "One response received"],
        "blockers": [],
        "dependencies": ["One-page offer"],
        "next_actions": ["Send first message"],
    }

    create_response = client.post("/mission-registry/create", json=payload)
    assert create_response.status_code == 200

    created = create_response.json()
    assert created["saved"] is True
    mission_id = created["mission"]["mission_id"]

    read_response = client.get(f"/mission-registry/{mission_id}")
    assert read_response.status_code == 200

    data = read_response.json()
    assert data["found"] is True
    assert data["mission"]["title"] == payload["title"]
    assert data["aar_count"] == 0


def test_list_registry_missions_filters_by_status():
    active_payload = {
        "title": "Active Mission",
        "objective": "Do active work.",
        "owner": "Kyle",
        "status": "active",
        "strategic_fit": 8,
        "roi": 8,
        "urgency": 8,
        "risk": 3,
        "difficulty": 4,
        "opportunity_cost": 2,
        "success_criteria": ["Done"],
    }

    blocked_payload = {
        "title": "Blocked Mission",
        "objective": "Blocked work.",
        "owner": "Kyle",
        "status": "blocked",
        "strategic_fit": 8,
        "roi": 8,
        "urgency": 8,
        "risk": 6,
        "difficulty": 6,
        "opportunity_cost": 4,
        "success_criteria": ["Unblocked"],
        "blockers": ["Need approval"],
    }

    client.post("/mission-registry/create", json=active_payload)
    client.post("/mission-registry/create", json=blocked_payload)

    response = client.get("/mission-registry/list?status=blocked")
    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 1
    assert data["missions"][0]["status"] == "blocked"


def test_update_status_and_add_aar():
    create_payload = {
        "title": "Finish Build Block",
        "objective": "Complete and save a Project Salus build module.",
        "owner": "Kyle",
        "status": "active",
        "deadline": "2026-07-05",
        "strategic_fit": 10,
        "roi": 8,
        "urgency": 9,
        "risk": 3,
        "difficulty": 5,
        "opportunity_cost": 2,
        "success_criteria": ["Tests pass", "Commit pushed"],
    }

    created = client.post("/mission-registry/create", json=create_payload).json()
    mission_id = created["mission"]["mission_id"]

    update_payload = {
        "mission_id": mission_id,
        "status": "completed",
        "progress_notes": ["357 tests passed."],
        "completed_criteria": ["Tests pass", "Commit pushed"],
        "blockers": [],
    }

    update_response = client.post("/mission-registry/update-status", json=update_payload)
    assert update_response.status_code == 200

    updated = update_response.json()
    assert updated["updated"] is True
    assert updated["mission"]["status"] == "completed"
    assert updated["next_action"] == "Run AAR and capture lessons learned."

    aar_payload = {
        "mission_id": mission_id,
        "title": "Finish Build Block",
        "effectiveness_score": 8,
        "what_went_well": ["Clean tests and clean push."],
        "what_failed": ["Manual paste errors earlier."],
        "lessons_learned": ["Use full paste blocks, not file paths."],
        "next_actions": ["Continue with persistence layer."],
        "doctrine_updates": ["Execution requires memory."],
    }

    aar_response = client.post("/mission-registry/aar", json=aar_payload)
    assert aar_response.status_code == 200

    aar = aar_response.json()
    assert aar["saved"] is True
    assert aar["aar"]["result"] == "effective"

    read_response = client.get(f"/mission-registry/{mission_id}")
    data = read_response.json()
    assert data["aar_count"] == 1


def test_dashboard_surfaces_blocked_missions():
    payload = {
        "title": "Blocked Governance Mission",
        "objective": "Deploy an AI tool without complete controls.",
        "owner": "Kyle",
        "status": "blocked",
        "deadline": "2026-07-10",
        "strategic_fit": 8,
        "roi": 8,
        "urgency": 6,
        "risk": 8,
        "difficulty": 7,
        "opportunity_cost": 5,
        "success_criteria": ["Controls implemented"],
        "blockers": ["No audit logging", "No kill switch"],
    }

    client.post("/mission-registry/create", json=payload)

    response = client.get("/mission-registry/dashboard/summary")
    assert response.status_code == 200

    data = response.json()
    assert data["total_missions"] == 1
    assert data["status_counts"]["blocked"] == 1
    assert "Blocked missions require command attention." in data["risk_flags"]
    assert data["next_action"] == "Unblock blocked missions first."
