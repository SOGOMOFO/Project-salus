from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_create_and_retrieve_sitrep():
    response = client.post(
        "/api/sitrep",
        json={
            "top_priority": "Build Daily SITREP loop",
            "blocker": "None",
            "action_1": "Create SITREP",
            "action_2": "Save to SQLite",
            "action_3": "Retrieve SITREP",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["sitrep"]["top_priority"] == "Build Daily SITREP loop"

    sitrep_id = data["sitrep"]["id"]

    get_response = client.get(f"/api/sitrep/{sitrep_id}")

    assert get_response.status_code == 200

    get_data = get_response.json()

    assert get_data["status"] == "ok"
    assert get_data["sitrep"]["id"] == sitrep_id
    assert get_data["sitrep"]["action_2"] == "Save to SQLite"


def test_list_sitreps():
    response = client.get("/api/sitrep")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "sitreps" in data
    assert isinstance(data["sitreps"], list)
