from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_family_readiness_endpoint():
    response = client.get("/family/readiness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "active"
    assert data["module"] == "Family Stability & Relationship Operating System"
