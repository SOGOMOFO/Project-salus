from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_strategy_critical_thinking_framework_loads():
    response = client.get("/strategy-critical-thinking/framework")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Project Salus Strategy & Critical Thinking Directorate"
    assert "PURSUE" in data["recommendations"]
    assert "assumption_quality" in data["reasoning_lenses"]


def test_strong_strategy_analysis_can_be_pursued():
    payload = {
        "title": "Echo Seven AI Governance Assessment Sprint",
        "objective": "Validate a paid AI governance and cyber readiness offer with small businesses.",
        "context": "This supports Echo Seven, Project Salus, cybersecurity, and federal contracting credibility.",
        "evidence_level": "strong_evidence",
        "strategic_fit": 10,
        "roi": 9,
        "risk": 4,
        "difficulty": 5,
        "opportunity_cost": 3,
        "time_horizon": "7 days",
        "assumptions": [
            "Small businesses are using AI without clear policies.",
            "Warm contacts will agree to short discovery calls.",
            "A narrow assessment is easier to sell than a broad AI consulting offer.",
        ],
        "evidence_for": [
            "AI adoption is increasing.",
            "Cyber and data exposure risks are real.",
            "Echo Seven needs a low-friction first offer.",
        ],
        "evidence_against": [
            "Some clients may not understand AI governance yet.",
        ],
        "constraints": [
            "Limited focus time.",
            "Need to keep WGU moving.",
        ],
        "dependencies": [
            "Clear one-page offer.",
            "Outreach list.",
        ],
        "alternatives": [
            "Build more Project Salus features first.",
            "Wait until more certifications are complete.",
        ],
        "failure_modes": [
            "Offer is too abstract.",
            "No one books a call.",
        ],
        "stakeholders": [
            "Kyle",
            "Echo Seven",
            "potential small business clients",
        ],
    }

    response = client.post("/strategy-critical-thinking/analyze", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["recommendation"] == "PURSUE"
    assert data["reasoning_score"] >= 70
    assert data["decision_memo"]["smallest_next_step"]
    assert data["red_team"]["attack_vectors"]


def test_unverified_high_risk_claim_is_discarded():
    payload = {
        "title": "Build Around AI Hidden Bible Code Claim",
        "objective": "Create a Project Salus doctrine around AI finding a hidden supernatural code.",
        "context": "Based on a viral video claim.",
        "evidence_level": "ai_generated_pattern",
        "strategic_fit": 2,
        "roi": 2,
        "risk": 9,
        "difficulty": 6,
        "opportunity_cost": 8,
        "time_horizon": "one sprint",
        "assumptions": [
            "The viral claim is accurate.",
            "The AI output proves something hidden.",
        ],
        "evidence_for": [
            "A video claimed it.",
        ],
        "evidence_against": [
            "No reproducible dataset.",
            "No independent review.",
            "LLMs can hallucinate patterns.",
        ],
        "constraints": [
            "Low credibility if treated as proof.",
        ],
        "dependencies": [],
        "alternatives": [
            "Use it only as a claim-verification training example.",
        ],
        "failure_modes": [
            "Salus becomes a hype machine.",
        ],
        "stakeholders": [
            "Kyle",
            "Project Salus",
        ],
    }

    response = client.post("/strategy-critical-thinking/analyze", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["recommendation"] == "DISCARD"
    assert data["evidence"]["requires_verification"] is True
    assert "Evidence requires verification before operational commitment." in data["warnings"]


def test_red_team_endpoint_returns_attack_vectors():
    payload = {
        "title": "Launch New Agent",
        "objective": "Add another expert agent to Project Salus.",
        "assumptions": [
            "More agents automatically make Salus smarter.",
            "The user will use the new agent regularly.",
        ],
        "constraints": [
            "Complexity is increasing.",
        ],
        "dependencies": [
            "Clean routing logic.",
        ],
        "failure_modes": [
            "Agent bloat.",
        ],
        "evidence_against": [
            "Too many agents can reduce usability.",
        ],
    }

    response = client.post("/strategy-critical-thinking/red-team", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "Launch New Agent"
    assert data["attack_vectors"]
    assert "enemy_vote" in data
    assert "Define the measurable outcome." in data["mitigation_actions"]


def test_strategy_analysis_warns_when_no_alternatives_or_failure_modes():
    payload = {
        "title": "Untested Idea",
        "objective": "Try a new idea without enough review.",
        "evidence_level": "expert_opinion",
        "strategic_fit": 6,
        "roi": 6,
        "risk": 5,
        "difficulty": 5,
        "opportunity_cost": 5,
        "time_horizon": "one sprint",
        "assumptions": [
            "This will probably work.",
        ],
        "evidence_for": [
            "Someone recommended it.",
        ],
        "evidence_against": [],
        "constraints": [],
        "dependencies": [],
        "alternatives": [],
        "failure_modes": [],
        "stakeholders": [],
    }

    response = client.post("/strategy-critical-thinking/analyze", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "No alternatives listed; decision may be under-compared." in data["warnings"]
    assert "No failure modes listed; plan may be overconfident." in data["warnings"]
