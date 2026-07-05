from pathlib import Path

from fastapi.testclient import TestClient

from backend.core.kernel_health import (
    EXPECTED_KERNEL_ROUTES,
    KERNEL_HEALTH_VERSION,
    kernel_architecture_summary,
    kernel_health_status,
    kernel_route_inventory,
)
from backend.main import app


client = TestClient(app)


def test_kernel_v10_health_route():
    response = client.get("/api/kernel/health")

    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "kernel_health"
    assert data["version"] == KERNEL_HEALTH_VERSION
    assert data["local_mvp_ready"] is True


def test_kernel_v10_route_inventory_route():
    response = client.get("/api/kernel/route-inventory")

    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "kernel_route_inventory"
    assert data["missing_count"] == 0


def test_kernel_v10_architecture_summary_route():
    response = client.get("/api/kernel/architecture-summary")

    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "kernel_architecture_summary"
    assert data["architecture"]["v1_0_status"] == "local_mvp_stabilized"


def test_kernel_v10_health_service():
    status = kernel_health_status()

    assert status["status"] == "ok"
    assert status["unhealthy_count"] == 0
    assert "execution_gate" in status["expected_modules"]


def test_kernel_v10_route_inventory_service():
    inventory = kernel_route_inventory(app)

    assert inventory["status"] == "ok"
    assert inventory["missing_count"] == 0
    assert len(EXPECTED_KERNEL_ROUTES) >= 16


def test_kernel_v10_architecture_summary_service():
    summary = kernel_architecture_summary()

    assert summary["status"] == "ok"
    assert "kernel_pipeline" in summary["architecture"]
    assert "Human Judgment System" in summary["architecture"]["identity"]


def test_kernel_v10_command_ui_still_loads():
    response = client.get("/command/kernel")

    assert response.status_code == 200
    assert "Kernel Command UI" in response.text
    assert "/api/kernel/orchestrate" in response.text


def test_kernel_v10_docs_exist():
    assert Path("SALUS_KERNEL_V1_0.md").exists()
    assert Path("PROJECT_SALUS_KERNEL_ARCHITECTURE_SUMMARY.md").exists()
    assert Path("CHECKPOINT_SALUS_KERNEL_V1_0_COMPLETE.md").exists()
    assert Path("SALUS_PHASE_III_PLAN.md").exists()
    assert Path("backend/core/kernel_health.py").exists()
