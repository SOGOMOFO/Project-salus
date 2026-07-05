from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def setup_function():
    client.post("/curiosity-parking-lot/reset")


def test_curiosity_parking_lot_framework_loads():
    response = client.get("/curiosity-parking-lot/framework")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Project Salus Curiosity Parking Lot & Backlog V1"
    assert data["core_rule"] == "Curiosity is not opportunity."


def test_park_and_read_item():
    payload = {
        "title": "Possible Future AI Video Idea",
        "summary": "Interesting but not tied to current mission.",
        "topics": ["ai", "business"],
        "claims": ["This may become useful later."],
        "strategic_fit": 5,
        "evidence_strength": 3,
        "actionability": 2,
        "roi": 4,
        "urgency": 1,
        "risk": 5,
        "opportunity_cost": 7,
    }
    created = client.post("/curiosity-parking-lot/park", json=payload).json()
    item_id = created["item"]["item_id"]
    response = client.get(f"/curiosity-parking-lot/{item_id}")
    assert response.status_code == 200
    assert response.json()["found"] is True


def test_list_filters_by_topic():
    client.post("/curiosity-parking-lot/park", json={"title": "AI Item", "summary": "AI backlog item.", "topics": ["ai"]})
    client.post("/curiosity-parking-lot/park", json={"title": "Wealth Item", "summary": "Wealth backlog item.", "topics": ["wealth"]})
    response = client.get("/curiosity-parking-lot/list?topic=wealth")
    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_review_promotes_item_to_mission_candidate():
    created = client.post(
        "/curiosity-parking-lot/park",
        json={
            "title": "Promising Echo Seven Offer Variant",
            "summary": "A narrower version may sell faster.",
            "topics": ["echo seven", "business"],
            "claims": ["Starter snapshot may convert better."],
        },
    ).json()
    item_id = created["item"]["item_id"]
    response = client.post(
        "/curiosity-parking-lot/review",
        json={
            "item_id": item_id,
            "evidence_strength": 8,
            "actionability": 9,
            "strategic_fit": 9,
            "roi": 9,
            "recommended_path": "mission",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["item"]["status"] == "promoted_to_mission"
    assert data["mission_candidate"]["title"].startswith("Validate parked item")


def test_review_promotes_item_to_doctrine_candidate():
    created = client.post(
        "/curiosity-parking-lot/park",
        json={
            "title": "Curiosity Is Not Opportunity",
            "summary": "Do not confuse interesting material with executable priorities.",
            "topics": ["doctrine", "strategy"],
            "claims": ["Curiosity is not opportunity."],
        },
    ).json()
    item_id = created["item"]["item_id"]
    response = client.post(
        "/curiosity-parking-lot/review",
        json={
            "item_id": item_id,
            "evidence_strength": 8,
            "actionability": 8,
            "strategic_fit": 9,
            "roi": 8,
            "recommended_path": "doctrine",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["item"]["status"] == "promoted_to_doctrine"
    assert data["doctrine_candidate"]["statement"] == "Curiosity is not opportunity."


def test_dashboard_surfaces_promote_and_discard_candidates():
    client.post("/curiosity-parking-lot/park", json={
        "title": "Promote Candidate", "summary": "High value now.", "strategic_fit": 10,
        "evidence_strength": 9, "actionability": 9, "roi": 9, "urgency": 8,
        "risk": 2, "opportunity_cost": 2
    })
    client.post("/curiosity-parking-lot/park", json={
        "title": "Discard Candidate", "summary": "Low value.", "strategic_fit": 1,
        "evidence_strength": 1, "actionability": 1, "roi": 1, "urgency": 1,
        "risk": 8, "opportunity_cost": 9
    })
    response = client.get("/curiosity-parking-lot/dashboard")
    assert response.status_code == 200
    data = response.json()
    assert data["promote_candidates"]
    assert data["discard_candidates"]
