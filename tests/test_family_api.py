from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_family_readiness_endpoint():
    response = client.get("/family/readiness")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "active"
    assert data["module"] == "Family Stability & Relationship Operating System"
    assert "weekly_family_aar" in data["standing_functions"]


def test_weekly_family_aar_endpoint():
    payload = {
        "went_well": ["Had one good conversation"],
        "missed_you": ["Did not check in enough"],
        "avoided_topics": ["money stress"],
        "needs_this_week": ["one calm budget conversation"],
        "building_together": ["family stability"],
    }

    response = client.post("/family/weekly-aar", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "family_readiness_score" in data
    assert data["risk_level"] in ["green", "amber", "red"]
    assert "avoided_topics_present" in data["risk_flags"]


def test_conflict_repair_endpoint():
    payload = {
        "issue": "Recurring argument about time and attention",
        "facts": ["Both people are busy"],
        "emotions": ["frustration"],
        "assumptions": ["I am not being prioritized"],
        "desired_repair": "Schedule one uninterrupted conversation",
    }

    response = client.post("/family/conflict-repair", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["issue"] == payload["issue"]
    assert "repair_protocol" in data
    assert data["recommended_language"]


def test_asset_protection_review_endpoint():
    payload = {
        "business_assets": ["Echo Seven Endeavors LLC", "Project Salus IP"],
        "personal_assets": ["home", "investment accounts"],
        "debts": ["truck loan"],
        "legal_documents": [],
        "unclear_boundaries": ["business ownership boundaries"],
    }

    response = client.post("/family/asset-protection-review", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "identified_gaps" in data
    assert "business_assets_require_structure_review" in data["identified_gaps"]