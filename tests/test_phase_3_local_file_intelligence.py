from fastapi.testclient import TestClient

from backend.main import app
from backend import mission_control_service as service


client = TestClient(app)
HEADERS = {"x-salus-token": "salus-local-token"}


def test_local_file_intelligence_reindex_service():
    result = service.reindex_local_file_intelligence(limit=50)
    assert result["status"] in {"ok", "partial"}
    assert result["indexed"] >= 1


def test_local_file_intelligence_state_service():
    service.reindex_local_file_intelligence(limit=50)
    state = service.get_local_file_intelligence_state()

    assert state["status"] == "ok"
    assert "counts" in state
    assert state["counts"]["indexed_files"] >= 1
    assert "files" in state


def test_local_file_intelligence_api_state():
    service.reindex_local_file_intelligence(limit=50)

    response = client.get("/api/mission-control/local-file-intelligence")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["counts"]["indexed_files"] >= 1


def test_local_file_intelligence_api_reindex():
    response = client.post("/api/mission-control/local-file-intelligence/reindex")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] in {"ok", "partial"}
    assert data["indexed"] >= 1


def test_local_file_intelligence_search():
    service.reindex_local_file_intelligence(limit=100)

    response = client.get("/api/mission-control/local-file-intelligence/search?q=mission")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "results" in data

