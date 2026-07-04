
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_09_charisma_status():
    response = client.get("/api/skills/charisma")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["module"] == "charisma_communication_skill"
    assert "presence" in data["skill_stack"]
    assert "ethical_influence" in data["skill_stack"]


def test_sprint_09_charisma_self_assessment():
    response = client.post(
        "/api/skills/charisma/self-assessment",
        json={
            "context": "GovCon client call",
            "presence": 7,
            "clarity": 6,
            "listening": 5,
            "emotional_control": 6,
            "confidence": 7,
            "empathy": 5,
            "framing": 6,
            "trust_building": 6,
            "ethical_alignment": 10,
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["assessment"]["average"] > 0
    assert data["assessment"]["weakest_field"]
    assert data["rule"].startswith("Charisma improves")


def test_sprint_09_charisma_daily_drill():
    response = client.get("/api/skills/charisma/daily-drill")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert "drill" in data
    assert "steps" in data["drill"]
    assert data["duration_minutes"] == 5


def test_sprint_09_charisma_conversation_aar():
    response = client.post(
        "/api/skills/charisma/conversation-aar",
        json={
            "objective": "Explain Project Salus clearly.",
            "audience": "Potential advisor",
            "what_i_said": "I explained the daily command system and learning modules.",
            "how_they_responded": "They understood the concept but asked about use cases.",
            "did_i_listen_well": "Mostly yes.",
            "did_i_stay_calm": "Yes.",
            "did_i_build_trust": "Somewhat.",
            "scorecard": {
                "presence": 7,
                "clarity": 7,
                "listening": 6,
                "emotional_control": 8,
                "confidence": 7,
                "empathy": 6,
                "framing": 6,
                "trust_building": 6,
                "ethical_alignment": 10,
            },
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["conversation_aar"]["objective"] == "Explain Project Salus clearly."
    assert data["conversation_aar"]["score"]["average"] > 0
    assert "teaching_point" in data
