from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_intelligence_intake_framework_loads():
    response = client.get("/intelligence-intake/framework")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Project Salus Intelligence Intake & Triage V1"
    assert "video" in data["source_types"]
    assert "decision_firewall" in data["routes"]


def test_hype_claim_requires_verification():
    payload = {
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
    }

    response = client.post("/intelligence-intake/triage", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["evidence_level"] == "ai_generated_pattern"
    assert "hype_term_detected:hidden" in data["risk_flags"]
    assert data["triage"]["recommendation"] == "VERIFY_FIRST"
    assert data["triage"]["recommended_route"] in ["decision_firewall", "ai_governance"]


def test_high_signal_business_item_creates_mission_candidate():
    payload = {
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
    }

    response = client.post("/intelligence-intake/triage", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["signal_score"] >= 65
    assert data["triage"]["recommendation"] == "CONVERT_TO_MISSION"
    assert data["mission_candidate"]["title"].startswith("Validate intelligence item")


def test_doctrine_topic_creates_doctrine_candidate():
    payload = {
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
    }

    response = client.post("/intelligence-intake/triage", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["triage"]["recommendation"] == "CONVERT_TO_DOCTRINE_CANDIDATE"
    assert data["doctrine_candidate"]["category"] == "mission_execution"


def test_low_signal_item_is_discarded_or_parked():
    payload = {
        "title": "Random Low Value Idea",
        "summary": "A vague idea with no evidence or action path.",
        "source_type": "social_post",
        "claims": [],
        "topics": ["misc"],
        "evidence_level": "unverified_claim",
        "strategic_fit": 1,
        "relevance": 2,
        "actionability": 1,
        "novelty": 2,
        "source_trust": 1,
        "risk": 5,
        "opportunity_cost": 8,
    }

    response = client.post("/intelligence-intake/triage", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["triage"]["recommendation"] in ["DISCARD", "PARK"]
    assert data["triage"]["recommended_route"] == "curiosity_parking_lot"


def test_batch_triage_counts_recommendations():
    payload = {
        "items": [
            {
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
            {
                "title": "Random Low Value Idea",
                "summary": "A vague idea with no evidence.",
                "source_type": "social_post",
                "topics": ["misc"],
                "evidence_level": "unverified_claim",
                "strategic_fit": 1,
                "relevance": 2,
                "actionability": 1,
                "novelty": 2,
                "source_trust": 1,
            },
        ],
    }

    response = client.post("/intelligence-intake/batch-triage", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["count"] == 2
    assert data["recommendation_counts"]["CONVERT_TO_MISSION"] == 1
    assert data["results"]
