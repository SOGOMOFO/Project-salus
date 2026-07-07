from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_snapshot_state_api():
    response = client.get("/api/mission-control/snapshots")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "snapshot_count" in data
    assert "snapshots" in data
    assert "snapshot_directory" in data
    assert "recommended_action" in data


def test_create_get_delete_snapshot_api():
    create = client.post(
        "/api/mission-control/snapshots",
        json={
            "label": "pytest_snapshot",
            "actor": "pytest",
        },
    )

    assert create.status_code == 200
    created = create.json()
    assert created["status"] == "created"
    assert created["snapshot_name"]

    snapshot_name = created["snapshot_name"]

    get_snapshot = client.get(f"/api/mission-control/snapshots/{snapshot_name}")
    assert get_snapshot.status_code == 200
    assert get_snapshot.json()["status"] == "ok"
    assert get_snapshot.json()["snapshot"]["snapshot_name"] == snapshot_name

    delete_snapshot = client.delete(f"/api/mission-control/snapshots/{snapshot_name}")
    assert delete_snapshot.status_code == 200
    assert delete_snapshot.json()["status"] == "deleted"


def test_restore_snapshot_api():
    create = client.post(
        "/api/mission-control/snapshots",
        json={
            "label": "restore_test_snapshot",
            "actor": "pytest",
        },
    )

    snapshot_name = create.json()["snapshot_name"]

    restore = client.post(f"/api/mission-control/snapshots/{snapshot_name}/restore")
    assert restore.status_code == 200
    assert restore.json()["status"] == "restored"
    assert restore.json()["snapshot_name"] == snapshot_name

    client.delete(f"/api/mission-control/snapshots/{snapshot_name}")


def test_snapshot_ui_panel_present():
    response = client.get("/mission-control/v1", headers={"x-salus-token": "salus-local-token"})
    assert response.status_code == 200

    assert "Snapshot Backup System" in response.text
    assert "/mission-control/snapshot" in response.text
    assert "/api/mission-control/snapshots" in response.text


def test_create_snapshot_from_ui():
    response = client.post(
        "/mission-control/snapshot",
        data={"label": "ui_snapshot_test"},
        follow_redirects=False,
    )

    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/v1"

    state = client.get("/api/mission-control/snapshots").json()
    assert any(
        "ui_snapshot_test" in snapshot["snapshot_name"]
        for snapshot in state["snapshots"]
    )
