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
    assert data["risk_level"] in ["green", "amber", "    assert data["risk_level"] in ["gse    assert data["risk_level"] in ["greenfli    assert data["risk_le  paylo    assert data["rise": "Re    assert data["risk_level"] inattent    assert data["risk_level"] in ["green", sy"],
        "emotions": ["frustration"],
        "assumptions": ["I am         "assumptions": ["I am       si        "assumptions": ["I am         "assumptions": ["I am       si        "acl        "assumptions": ["I am         "assumptions": ["I ssert response.status_code == 200

    data =    data =   n()    data =    data =   n()    data =    data =     assert "repair_protocol" in data
    assert data["recommended_language"]


def test_asset_protecdef test_asset_protecdef test_asset_protecdef test_assess_assdef test_asset_protecdef test_asset_protecdef tus IP"],
                                                          ,
                                         "lega                          "unclear_boundaries": ["business ownership bou                                         "lega                          "unclear_boundaries": ["business ownership bou                                         "lega                          "unclear_boundaries": ["business ownership bou                                      gaps"]
