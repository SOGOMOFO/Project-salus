from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_daily_start_creates_sitrep():
    response = client.post(
        "/api/daily/start",
        json={
            "top_priority": "Build Daily Operations Block",
            "blocker": "None",
            "action_1": "Write endpoint",
            "action_2": "Run tests",
            "action_3": "Commit code",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "started"
    assert data["message"] == "Daily operating cycle started."
    assert data["sitrep"]["top_priority"] == "Build Daily Operations Block"
    assert "next_recommended_action" in data


def test_daily_closeout_creates_aar():
    response = client.post(
        "/api/daily/closeout",
        json={
            "mission": "Daily Operations Block",
            "what_happened": "Built daily endpoints.",
            "what_worked": "Batch build method.",
            "what_failed": "Nothing major.",
            "lesson_learned": "Batching endpoints speeds development.",
            "next_action": "Build dashboard layer.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "closed"
    assert data["message"] == "Daily operating cycle closed."
    assert data["aar"]["mission"] == "Daily Operations Block"
    assert "next_recommended_action" in data


def test_daily_history_returns_sitreps_and_aars():
    response = client.get("/api/daily/history")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert "history" in data
    assert "sitreps" in data["history"]
    assert "aars" in data["history"]
    assert "counts" in data["history"]
    assert isinstance(data["history"]["sitreps"], list)
    assert isinstance(data["history"]["aars"], list)
