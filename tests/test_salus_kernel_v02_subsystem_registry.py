from pathlib import Path

from fastapi.testclient import TestClient

from backend.core.kernel import kernel_status, route_request
from backend.core.subsystem_registry import (
    get_subsystem,
    list_subsystems,
    route_for_intent,
    subsystem_registry_status,
)
from backend.main import app


client = TestClient(app)


def test_kernel_v02_subsystem_registry_status_route():
    response = client.get("/api/kernel/subsystem-registry/status")

    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "subsystem_registry"
    assert data["subsystem_count"] >= 5


def test_kernel_v02_list_subsystems_route():
    response = client.get("/api/kernel/subsystems")

    assert response.status_code == 200
    data = response.json()
    ids = {subsystem["id"] for subsystem in data["subsystems"]}
    assert "core_identity" in ids
    assert "knowledge" in ids
    assert "memory" in ids
    assert "judgment" in ids


def test_kernel_v02_get_subsystem_route():
    response = client.get("/api/kernel/subsystems/judgment")

    assert response.status_code == 200
    assert response.json()["subsystem"]["status_route"] == "/api/judgment-engine/status"


def test_kernel_v02_route_request_selects_subsystem():
    result = route_request({"input": "Should I pursue this decision?"})

    assert result["classification"]["intent"] == "judgment"
    assert result["selected_subsystem"]["subsystem_id"] == "judgment"


def test_kernel_v02_intent_mapping():
    assert route_for_intent("memory")["subsystem_id"] == "memory"
    assert route_for_intent("learning")["subsystem_id"] == "knowledge"
    assert route_for_intent("general")["subsystem_id"] == "core_identity"


def test_kernel_v02_status_includes_registry():
    status = kernel_status()

    assert "subsystem_registry" in status
    assert status["subsystem_registry"]["subsystem_count"] >= 5


def test_kernel_v02_docs_exist():
    assert Path("SALUS_KERNEL_V0_2.md").exists()
    assert Path("backend/core/subsystem_registry.py").exists()
    assert get_subsystem("kernel") is not None
    assert len(list_subsystems()) >= 5
    assert subsystem_registry_status()["status"] == "ok"
