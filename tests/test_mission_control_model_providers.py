from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_model_provider_state_defaults():
    response = client.get("/api/mission-control/model-providers")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "counts" in data
    assert isinstance(data["providers"], list)
    assert isinstance(data["routes"], list)

    providers = {provider["provider_key"] for provider in data["providers"]}
    assert "local_placeholder" in providers
    assert "openai_future" in providers
    assert "local_llm_future" in providers

    routes = {route["route_key"] for route in data["routes"]}
    assert "general_reasoning" in routes


def test_upsert_model_provider_api():
    response = client.post(
        "/api/mission-control/model-providers/providers",
        json={
            "provider_key": "pytest_model_provider",
            "name": "Pytest Model Provider",
            "provider_type": "test_model",
            "status": "planned",
            "enabled": True,
            "priority": 9,
            "permission_level": "local_model_runtime",
            "config_summary": "Test provider.",
            "actor": "pytest",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "saved"
    assert response.json()["provider"]["provider_key"] == "pytest_model_provider"
    assert response.json()["provider"]["enabled"] == 1


def test_upsert_model_route_api():
    response = client.post(
        "/api/mission-control/model-providers/routes",
        json={
            "route_key": "pytest_reasoning_route",
            "purpose": "Pytest route",
            "primary_provider": "local_placeholder",
            "fallback_provider": "local_placeholder",
            "policy": "test policy",
            "enabled": True,
            "actor": "pytest",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "saved"
    assert response.json()["route"]["route_key"] == "pytest_reasoning_route"


def test_create_local_reasoning_request_api():
    response = client.post(
        "/api/mission-control/model-providers/reasoning",
        json={
            "route_key": "general_reasoning",
            "prompt": "Create a mission plan for today.",
            "context": "Testing local placeholder.",
            "requested_by": "pytest",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "created"
    assert data["request"]["status"] == "completed"
    assert data["request"]["provider_used"] == "local_placeholder"
    assert data["request"]["parsed_result"]["status"] == "ok"
    assert "recommendation" in data["request"]["parsed_result"]


def test_reasoning_requests_list_api():
    response = client.get("/api/mission-control/model-providers/reasoning")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["requests"], list)


def test_model_provider_ui_panel_present():
    response = client.get("/mission-control/v1", headers={"x-salus-token": "salus-local-token"})
    assert response.status_code == 200

    assert "Model Provider Router" in response.text
    assert "/mission-control/model-provider/reasoning" in response.text
    assert "/api/mission-control/model-providers" in response.text


def test_model_provider_ui_reasoning_request():
    response = client.post(
        "/mission-control/model-provider/reasoning",
        data={
            "route_key": "general_reasoning",
            "prompt": "Brief the commander.",
            "context": "UI test.",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/v1"
