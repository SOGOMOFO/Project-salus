from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_background_job_state_defaults():
    response = client.get("/api/mission-control/background-jobs")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "counts" in data
    assert isinstance(data["jobs"], list)

    keys = {job["job_key"] for job in data["jobs"]}
    assert "morning_command_loop" in keys
    assert "evening_aar_loop" in keys
    assert "snapshot_checkpoint" in keys
    assert "agent_runtime_sweep" in keys
    assert "health_contract_check" in keys


def test_run_health_background_job():
    response = client.post("/api/mission-control/background-jobs/health_contract_check/run")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "completed"
    assert data["job_key"] == "health_contract_check"
    assert "result" in data


def test_background_job_enable_disable():
    disabled = client.post("/api/mission-control/background-jobs/agent_runtime_sweep/disable")
    assert disabled.status_code == 200
    assert disabled.json()["status"] == "disabled"
    assert disabled.json()["job"]["enabled"] == 0

    enabled = client.post("/api/mission-control/background-jobs/agent_runtime_sweep/enable")
    assert enabled.status_code == 200
    assert enabled.json()["status"] == "enabled"
    assert enabled.json()["job"]["enabled"] == 1


def test_background_job_sweep():
    response = client.post("/api/mission-control/background-jobs/sweep")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "completed"
    assert data["mode"] == "safe_sweep"
    assert "results" in data


def test_background_job_runs_api():
    response = client.get("/api/mission-control/background-jobs/runs")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["runs"], list)


def test_background_job_ui_panel_present():
    response = client.get("/mission-control/v1", headers={"x-salus-token": "salus-local-token"})
    assert response.status_code == 200

    assert "Background Job Scheduler" in response.text
    assert "/mission-control/background-job/sweep" in response.text
    assert "/api/mission-control/background-jobs" in response.text


def test_background_job_ui_run():
    response = client.post(
        "/mission-control/background-job/health_contract_check/run",
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/v1"
