from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_tool_adapter_state_api_defaults():
    response = client.get("/api/mission-control/tool-adapters")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "counts" in data
    assert isinstance(data["adapters"], list)

    keys = {adapter["adapter_key"] for adapter in data["adapters"]}
    assert "local_files" in keys
    assert "gmail_adapter" in keys
    assert "calendar_adapter" in keys


def test_local_file_adapter_list_files():
    response = client.post(
        "/api/mission-control/tool-adapters/local_files/actions/list_project_files",
        json={"path": "."},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["action"] == "list_project_files"
    assert isinstance(data["files"], list)


def test_local_file_adapter_summarize_file():
    response = client.post(
        "/api/mission-control/tool-adapters/local_files/actions/summarize_project_file",
        json={"path": "backend/main.py"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["action"] == "summarize_project_file"
    assert "summary" in data


def test_local_file_adapter_blocks_path_escape():
    response = client.post(
        "/api/mission-control/tool-adapters/local_files/actions/list_project_files",
        json={"path": "../"},
    )

    assert response.status_code == 500 or response.json()["status"] in {"blocked", "error"}


def test_adapter_action_not_allowed():
    response = client.post(
        "/api/mission-control/tool-adapters/local_files/actions/delete_file",
        json={"path": "backend/main.py"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "action_not_allowed"


def test_external_adapter_requires_firewall_approval():
    client.post("/api/mission-control/tool-adapters/gmail_adapter/enable")

    response = client.post(
        "/api/mission-control/tool-adapters/gmail_adapter/actions/draft_email",
        json={"to": "test@example.com", "body": "draft only"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "pending_firewall_approval"
    assert response.json()["firewall_action_id"]


def test_tool_adapter_runs_api():
    response = client.get("/api/mission-control/tool-adapters/runs")
    assert response.status_code == 200

    assert response.json()["status"] == "ok"
    assert isinstance(response.json()["runs"], list)


def test_tool_adapter_ui_panel_present():
    response = client.get("/mission-control/v1", headers={"x-salus-token": "salus-local-token"})
    assert response.status_code == 200

    assert "Tool Adapter Interface" in response.text
    assert "/mission-control/tool-adapter/local_files/actions/list_project_files" in response.text
    assert "/api/mission-control/tool-adapters" in response.text


def test_tool_adapter_ui_execute_local_action():
    response = client.post(
        "/mission-control/tool-adapter/local_files/actions/list_project_files",
        data={"path": "."},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/v1"
