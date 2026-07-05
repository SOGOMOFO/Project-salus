from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def setup_function():
    client.post("/workflow-orchestrator/reset")
    client.post("/mission-registry/reset")
    client.post("/doctrine-registry/reset")
    client.post("/curiosity-parking-lot/reset")


def test_workflow_orchestrator_framework_loads():
    response = client.get("/workflow-orchestrator/framework")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Project Salus Workflow Orchestrator V1"
    assert "intelligence_to_action" in data["workflow_types"]
    assert "mission_created" in data["workflow_actions"]


def test_high_signal_intelligence_creates_mission_registry_record():
    payload = {
        "item": {
            "title": "AI Governance Assessment Offer",
            "summary": "Small businesses need practical AI and cyber readiness assessments.",
            "source_type": "conversation",
            "claims": ["Small businesses are using AI without clear policies."],
            "topics": ["business", "echo seven"],
            "evidence_level": "strong_evidence",
            "strategic_fit": 10,
            "relevance": 10,
            "actionability": 9,
            "novelty": 6,
            "source_trust": 8,
            "roi": 9,
            "urgency": 8,
            "risk": 4,
            "difficulty": 5,
            "opportunity_cost": 3,
        },
        "auto_create_records": True,
    }

    response = client.post("/workflow-orchestrator/intelligence-to-action", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["triage_recommendation"] == "CONVERT_TO_MISSION"
    assert "mission_created" in data["actions_taken"]
    assert data["created_records"]["mission"]["mission_id"].startswith("mission_")

    missions = client.get("/mission-registry/list").json()
    assert missions["count"] == 1


def test_doctrine_intelligence_creates_doctrine_record():
    payload = {
        "item": {
            "title": "Execution Requires Memory",
            "summary": "Lessons from missions should become persistent doctrine.",
            "source_type": "internal_note",
            "claims": ["Mission lessons should be converted into doctrine after AAR."],
            "topics": ["doctrine", "mission"],
            "evidence_level": "expert_opinion",
            "strategic_fit": 9,
            "relevance": 9,
            "actionability": 8,
            "novelty": 5,
            "source_trust": 8,
            "roi": 7,
            "urgency": 6,
            "risk": 3,
            "difficulty": 4,
            "opportunity_cost": 2,
        },
        "auto_create_records": True,
    }

    response = client.post("/workflow-orchestrator/intelligence-to-action", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["triage_recommendation"] == "CONVERT_TO_DOCTRINE_CANDIDATE"
    assert "doctrine_created" in data["actions_taken"]
    assert data["created_records"]["doctrine"]["doctrine_id"].startswith("doc_")

    doctrine = client.get("/doctrine-registry/list").json()
    assert doctrine["count"] == 1


def test_verify_first_item_is_parked_for_review():
    payload = {
        "item": {
            "title": "AI Decoded Hidden Biblical Code and Terrified Researchers",
            "summary": "A viral video claims Grok decoded a hidden structure in scripture.",
            "source_type": "video",
            "claims": ["Grok discovered a supernatural hidden code."],
            "topics": ["ai", "religion", "critical thinking"],
            "evidence_level": "ai_generated_pattern",
            "strategic_fit": 3,
            "relevance": 6,
            "actionability": 2,
            "novelty": 7,
            "source_trust": 2,
            "risk": 8,
            "opportunity_cost": 7,
        },
        "auto_create_records": True,
        "park_verify_items": True,
    }

    response = client.post("/workflow-orchestrator/intelligence-to-action", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["triage_recommendation"] == "VERIFY_FIRST"
    assert "parked" in data["actions_taken"]
    assert data["created_records"]["parking_lot_item"]["item_id"].startswith("park_")

    parked = client.get("/curiosity-parking-lot/list").json()
    assert parked["count"] == 1


def test_manual_candidate_mission_creation():
    payload = {
        "mission_candidate": {
            "title": "Validate parked item: Starter Snapshot",
            "objective": "Test whether a starter snapshot sells faster.",
            "source": "curiosity_parking_lot",
            "owner": "Kyle",
            "status": "planned",
            "strategic_fit": 9,
            "roi": 9,
            "urgency": 7,
            "risk": 4,
            "difficulty": 5,
            "opportunity_cost": 3,
            "success_criteria": ["Three prospects contacted"],
            "next_actions": ["Send short outreach"],
        },
        "source_item": {"title": "Starter Snapshot idea"},
    }

    response = client.post("/workflow-orchestrator/create-mission-from-candidate", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "mission_created" in data["actions_taken"]
    assert data["created_records"]["mission"]["title"] == "Validate parked item: Starter Snapshot"


def test_workflow_dashboard_counts_runs():
    client.post(
        "/workflow-orchestrator/intelligence-to-action",
        json={
            "item": {
                "title": "AI Governance Assessment Offer",
                "summary": "Small businesses need practical AI and cyber readiness assessments.",
                "source_type": "conversation",
                "claims": ["Small businesses are using AI without clear policies."],
                "topics": ["business", "echo seven"],
                "evidence_level": "strong_evidence",
                "strategic_fit": 10,
                "relevance": 10,
                "actionability": 9,
                "source_trust": 8,
                "roi": 9,
                "urgency": 8,
                "risk": 4,
                "difficulty": 5,
                "opportunity_cost": 3,
            }
        },
    )

    response = client.get("/workflow-orchestrator/dashboard")
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "workflow_orchestrator_dashboard"
    assert data["total_runs"] == 1
    assert data["action_counts"]["mission_created"] == 1
