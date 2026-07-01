from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_mvp_status_endpoint_returns_operating_loop():
    response = client.get("/api/mvp/status")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "ok"
    assert data["mvp"]["heartbeat"] == "alive"

    assert "loop" in data["mvp"]
    assert "capabilities" in data["mvp"]
    assert "counts" in data["mvp"]

    assert data["mvp"]["capabilities"]["judgment_api"] is True
    assert data["mvp"]["capabilities"]["daily_sitrep"] is True
    assert data["mvp"]["capabilities"]["mission_tracker"] is True
    assert data["mvp"]["capabilities"]["aar_log"] is True
    assert data["mvp"]["capabilities"]["sqlite_persistence"] is True
