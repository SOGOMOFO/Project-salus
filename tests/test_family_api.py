from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def reset_family_data():
    response = client.post(
        "/family/reset",
        json={"confirmation": "RESET_FAMILY_STABILITY_DEV_DATA"},
    )
    assert response.status_code == 200


def test_family_readiness_endpoint():
    response = client.get("/family/readiness")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "active"
    assert data["module"] == "Family Stability & Relationship Operating System"
    assert "weekly_family_aar" in data["standing_functions"]
    assert "family_history" in data["standing_functions"]
    assert data["doctrine"]["relationship_health"] == "core_asset"


def test_family_status_endpoint():
    reset_family_data()

    response = client.get("/family/status")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["module"] == "family_stability"
    assert data["operating_mode"] == "preventive"
    assert data["records"]["weekly_aars"] == 0
    assert "next_action" in data


def test_weekly_family_aar_endpoint_stores_record():
    reset_family_data()

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
    assert data["stored"] is True
    assert data["record_id"]

    history = client.get("/family/history").json()
    assert history["counts"]["weekly_aars"] == 1


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
    assert "assumptions_present" in data["escalation_risks"]


def test_asset_protection_review_endpoint_stores_record():
    reset_family_data()

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
    assert "personal_assets_without_documented_plan" in data["identified_gaps"]
    assert data["stored"] is True

    history = client.get("/family/history").json()
    assert history["counts"]["asset_reviews"] == 1


def test_household_alignment_endpoint_stores_record():
    reset_family_data()

    payload = {
        "top_family_priority": "Stabilize household schedule and money conversations",
        "household_stressors": ["busy week"],
        "money_topics": ["budget review"],
        "parenting_topics": ["school planning"],
        "schedule_conflicts": ["work and family time"],
        "business_impacts": ["Echo Seven planning time"],
        "next_family_actions": ["Schedule one budget conversation"],
    }

    response = client.post("/family/household-alignment", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert "alignment_score" in data
    assert data["risk_level"] in ["green", "amber", "red"]
    assert "money_topics_present" in data["risk_flags"]
    assert data["stored"] is True

    history = client.get("/family/history").json()
    assert history["counts"]["household_alignments"] == 1


def test_family_history_endpoint():
    reset_family_data()

    response = client.get("/family/history")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["module"] == "family_history"
    assert data["counts"]["weekly_aars"] == 0
    assert "records" in data


def test_family_reset_requires_confirmation():
    response = client.post("/family/reset", json={"confirmation": "wrong"})
    assert response.status_code == 400


def test_family_dashboard_endpoint():
    response = client.get("/family/dashboard")
    assert response.status_code == 200
    assert "Project Salus" in response.text
    assert "Family Stability" in response.text
    assert "Family History" in response.text
