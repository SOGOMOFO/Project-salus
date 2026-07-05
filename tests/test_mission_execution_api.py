from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_mission_execution_framework_loads():
    response = client.get("/mission-execution/framework")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Project Salus Mission Execution Engine V1"
    assert "active" in data["statuses"]
    assert "EXECUTE_NOW" in data["recommendations"]


def test_high_priority_mission_can_execute_now():
    payload = {
        "title": "Run Echo Seven Assessment Outreach",
        "objective": "Contact three warm leads for the AI Governance & Cyber Readiness Assessment.",
        "source": "strategy_critical_thinking",
        "owner": "Kyle",
        "status": "planned",
        "deadline": "2026-07-06",
        "strategic_fit": 10,
        "roi": 9,
        "urgency": 8,
        "risk": 3,
        "difficulty": 4,
        "opportunity_cost": 2,
        "success_criteria": [
            "Three outreach messages sent",
            "One discovery call requested",
        ],
        "blockers": [],
        "dependencies": [
            "One-page offer",
        ],
        "next_actions": [
            "Write outreach message",
        ],
    }

    response = client.post("/mission-execution/create", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["recommendation"] == "EXECUTE_NOW"
    assert data["ready_to_execute"] is True
    assert data["priority_level"] in ["critical", "high"]
    assert data["mission_id"].startswith("mission_")


def test_blocked_mission_requires_unblock_first():
    payload = {
        "title": "Deploy Autonomous Business Agent",
        "objective": "Allow agent to send emails and update records.",
        "source": "ai_governance",
        "owner": "Kyle",
        "status": "planned",
        "deadline": "2026-07-10",
        "strategic_fit": 8,
        "roi": 8,
        "urgency": 6,
        "risk": 8,
        "difficulty": 7,
        "opportunity_cost": 5,
        "success_criteria": [
            "Audit logging enabled",
        ],
        "blockers": [
            "No kill switch",
            "No human approval gate",
        ],
        "dependencies": [],
        "next_actions": [],
    }

    response = client.post("/mission-execution/create", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["recommendation"] == "UNBLOCK_FIRST"
    assert data["ready_to_execute"] is False
    assert "active_blockers_present" in data["execution_gaps"]


def test_status_update_for_completed_mission_recommends_aar():
    payload = {
        "mission_id": "mission_test123",
        "title": "Finish Build Block",
        "status": "completed",
        "progress_notes": [
            "Tests passed and commit pushed.",
        ],
        "completed_criteria": [
            "Full test suite passed.",
        ],
        "blockers": [],
    }

    response = client.post("/mission-execution/update-status", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "completed"
    assert data["next_action"] == "Run AAR and capture lessons learned."


def test_sprint_plan_selects_highest_priority_missions():
    payload = {
        "sprint_name": "Salus Execution Sprint",
        "capacity": 1,
        "missions": [
            {
                "title": "Low Priority Cleanup",
                "objective": "Clean up minor notes.",
                "source": "manual",
                "owner": "Kyle",
                "status": "planned",
                "deadline": "2026-07-08",
                "strategic_fit": 3,
                "roi": 2,
                "urgency": 2,
                "risk": 2,
                "difficulty": 2,
                "opportunity_cost": 2,
                "success_criteria": ["Notes reviewed"],
                "blockers": [],
                "dependencies": [],
                "next_actions": [],
            },
            {
                "title": "High Priority Echo Seven Outreach",
                "objective": "Validate the first paid offer.",
                "source": "strategy_critical_thinking",
                "owner": "Kyle",
                "status": "planned",
                "deadline": "2026-07-06",
                "strategic_fit": 10,
                "roi": 9,
                "urgency": 9,
                "risk": 3,
                "difficulty": 4,
                "opportunity_cost": 2,
                "success_criteria": ["Three leads contacted"],
                "blockers": [],
                "dependencies": [],
                "next_actions": [],
            },
        ],
    }

    response = client.post("/mission-execution/sprint-plan", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert len(data["selected_missions"]) == 1
    assert data["selected_missions"][0]["title"] == "High Priority Echo Seven Outreach"
    assert "Sprint demand exceeds stated capacity." in data["risk_flags"]


def test_mission_aar_captures_lessons_and_next_actions():
    payload = {
        "mission_id": "mission_test123",
        "title": "Run Outreach Sprint",
        "effectiveness_score": 8,
        "what_went_well": [
            "Offer was clear.",
        ],
        "what_failed": [
            "Message was too long.",
        ],
        "lessons_learned": [
            "Shorter outreach gets faster responses.",
        ],
        "next_actions": [
            "Rewrite message shorter.",
        ],
        "doctrine_updates": [
            "Use short outreach before long explanations.",
        ],
    }

    response = client.post("/mission-execution/aar", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["result"] == "effective"
    assert data["aar_flags"] == []
    assert data["next_action"] == "Feed lessons learned back into strategy, daily brief, and future sprint planning."
