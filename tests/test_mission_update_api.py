from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)

HEADERS = {
    "x-salus-passphrase": "salus-secure",
    "x-salus-role": "commander",
}


def test_update_core_mission():
    create_response = client.post(
        "/core/missions",
        headers=HEADERS,
        json={
            "title": "Mission Update Test",
            "description": "Initial mission",
            "priority": "low",
        },
    )

    assert create_response.status_code == 200

    created = create_response.json()
    assert created["status"] == "created"

    mission_id = created["mission"]["id"]

    update_response = client.patch(
        f"/core/missions/{mission_id}",
        headers=HEADERS,
        json={
            "description": "Updated mission details",
            "priority": "high",
            "status": "blocked",
        },
    )

    assert update_response.status_code == 200

    updated = update_response.json()

    assert updated["status"] == "updated"
    assert updated["mission"]["id"] == mission_id
    assert updated["mission"]["title"] == "Mission Update Test"
    assert updated["mission"]["description"] == "Updated mission details"
    assert updated["mission"]["priority"] == "high"
    assert updated["mission"]["status"] == "blocked"


def test_update_missing_core_mission_returns_not_found():
    response = client.patch(
        "/core/missions/999999",
        headers=HEADERS,
        json={"status": "paused"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "not_found"
