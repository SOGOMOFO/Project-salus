from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_create_and_retrieve_aar():
    response = client.post(
        "/api/aar",
        json={
            "mission": "Build AAR loop",
            "what_happened": "Created AAR persistence and API routes.",
            "what_worked": "Service and endpoint structure matched SITREP pattern.",
            "what_failed": "No failure.",
            "lesson_learned": "AAR closes the daily operating loop.",
            "next_action": "Connect AAR to dashboard later.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["aar"]["mission"] == "Build AAR loop"
    assert data["aar"]["lesson_learned"] == "AAR closes the daily operating loop."

    aar_id = data["aar"]["id"]

    get_response = client.get(f"/api/aar/{aar_id}")

    assert get_response.status_code == 200

    get_data = get_response.json()

    assert get_data["status"] == "ok"
    assert get_data["aar"]["id"] == aar_id
    assert get_data["aar"]["next_action"] == "Connect AAR to dashboard later."


def test_list_aars():
    response = client.get("/api/aar")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "aars" in data
    assert isinstance(data["aars"], list)
