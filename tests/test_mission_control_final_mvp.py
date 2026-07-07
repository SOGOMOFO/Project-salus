from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_records_api_create_and_list():
    create = client.post(
        "/api/mission-control/records",
        json={
            "record_type": "decision",
            "title": "Final MVP Record Test",
            "content": "This verifies records link-in.",
            "source": "pytest",
            "tags": "mvp,test",
        },
    )

    assert create.status_code == 200
    assert create.json()["status"] == "created"
    assert create.json()["record"]["title"] == "Final MVP Record Test"

    listed = client.get("/api/mission-control/records")
    assert listed.status_code == 200
    assert listed.json()["status"] == "ok"
    assert any(record["title"] == "Final MVP Record Test" for record in listed.json()["records"])


def test_daily_loop_api():
    create = client.post("/api/mission-control/daily-loop/full_cycle")
    assert create.status_code == 200
    assert create.json()["status"] == "created"
    assert create.json()["daily_loop"]["loop_type"] == "full_cycle"

    listed = client.get("/api/mission-control/daily-loop")
    assert listed.status_code == 200
    assert listed.json()["status"] == "ok"
    assert isinstance(listed.json()["daily_loops"], list)


def test_command_state_export_api():
    response = client.get("/api/mission-control/export")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "mission_control" in data
    assert "agent_execution" in data
    assert "agent_risk" in data
    assert "records" in data
    assert "daily_loops" in data
    assert "audit_log" in data


def test_local_mvp_readiness_api():
    response = client.get("/api/mission-control/mvp-readiness")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] in {"ready", "degraded"}
    assert "checks" in data
    assert "failed_checks" in data
    assert "recommended_action" in data


def test_v1_contains_final_mvp_panels():
    response = client.get("/mission-control/v1")
    assert response.status_code == 200

    assert "Memory / Records Link-In" in response.text
    assert "Daily Operating Loop" in response.text
    assert "Export Command State" in response.text
    assert "MVP Readiness" in response.text


def test_create_record_from_ui():
    response = client.post(
        "/mission-control/record",
        data={
            "record_type": "note",
            "title": "UI Final MVP Record",
            "content": "Created from UI.",
            "tags": "ui,mvp",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/v1"


def test_create_daily_loop_from_ui():
    response = client.post(
        "/mission-control/daily-loop/morning",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/v1"
