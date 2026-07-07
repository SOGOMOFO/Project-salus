from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_connector_registry_defaults():
    response = client.get("/api/mission-control/connectors")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "counts" in data
    assert isinstance(data["connectors"], list)

    keys = {connector["connector_key"] for connector in data["connectors"]}
    assert "gmail" in keys
    assert "google_calendar" in keys
    assert "files" in keys
    assert "finance" in keys


def test_upsert_connector_api():
    response = client.post(
        "/api/mission-control/connectors",
        json={
            "connector_key": "pytest_connector",
            "name": "Pytest Connector",
            "connector_type": "test",
            "status": "planned",
            "permission_level": "external_read",
            "enabled": True,
            "config_summary": "Created during tests.",
            "actor": "pytest",
        },
    )

    assert response.status_code == 200
    assert response.json()["status"] == "saved"
    assert response.json()["connector"]["connector_key"] == "pytest_connector"
    assert response.json()["connector"]["enabled"] == 1


def test_connector_enable_disable_status_api():
    client.post(
        "/api/mission-control/connectors",
        json={
            "connector_key": "pytest_status_connector",
            "name": "Pytest Status Connector",
            "connector_type": "test",
            "status": "planned",
            "permission_level": "external_read",
            "enabled": False,
        },
    )

    enabled = client.post("/api/mission-control/connectors/pytest_status_connector/enable")
    assert enabled.status_code == 200
    assert enabled.json()["status"] == "enabled"
    assert enabled.json()["connector"]["enabled"] == 1

    ready = client.post(
        "/api/mission-control/connectors/pytest_status_connector/status/local_ready",
        json={"detail": "pytest marked ready"},
    )
    assert ready.status_code == 200
    assert ready.json()["status"] == "updated"
    assert ready.json()["connector"]["status"] == "local_ready"

    disabled = client.post("/api/mission-control/connectors/pytest_status_connector/disable")
    assert disabled.status_code == 200
    assert disabled.json()["status"] == "disabled"
    assert disabled.json()["connector"]["enabled"] == 0


def test_connector_events_api():
    response = client.get("/api/mission-control/connectors/events")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert isinstance(data["events"], list)


def test_connector_ui_panel_present():
    response = client.get("/mission-control/v1", headers={"x-salus-token": "salus-local-token"})
    assert response.status_code == 200

    assert "Connector Registry" in response.text
    assert "/mission-control/connector" in response.text
    assert "/api/mission-control/connectors" in response.text


def test_create_connector_from_ui():
    response = client.post(
        "/mission-control/connector",
        data={
            "connector_key": "ui_connector",
            "name": "UI Connector",
            "connector_type": "test",
            "status": "planned",
            "permission_level": "external_read",
            "enabled": "1",
            "config_summary": "Created from UI.",
        },
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/v1"

    connector = client.get("/api/mission-control/connectors/ui_connector")
    assert connector.status_code == 200
    assert connector.json()["status"] == "ok"
    assert connector.json()["connector"]["enabled"] == 1
