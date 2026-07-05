from pathlib import Path

from fastapi.testclient import TestClient

from backend.core.kernel import (
    KERNEL_VERSION,
    classify_intent,
    kernel_architecture,
    kernel_status,
    route_request,
)
from backend.main import app


client = TestClient(app)


def test_kernel_status_route():
    response = client.get("/api/kernel/status")

    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "salus_kernel"
    assert data["version"] == KERNEL_VERSION
    assert "Human Judgment System" in data["identity"]


def test_kernel_architecture_route():
    response = client.get("/api/kernel/architecture")

    assert response.status_code == 200
    data = response.json()
    assert data["architecture"]["kernel"] == "central orchestrator"
    assert "memory" in data["architecture"]["layers"]


def test_kernel_route_learning_intent():
    response = client.post(
        "/api/kernel/route",
        json={"user": "Kyle", "input": "Help me study WGU cybersecurity."},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["classification"]["intent"] == "learning"
    assert data["classification"]["layer"] == "learning"


def test_kernel_route_judgment_requires_approval():
    result = route_request({"input": "Should I pursue this business idea?"})

    assert result["classification"]["intent"] == "judgment"
    assert result["approval_required"] is True


def test_kernel_classify_memory():
    result = classify_intent("Remember this mission context.")

    assert result["intent"] == "memory"
    assert result["layer"] == "memory"


def test_kernel_page_loads():
    response = client.get("/command/kernel")

    assert response.status_code == 200
    assert "Project Salus" in response.text
    assert "Kernel" in response.text


def test_kernel_docs_exist():
    assert Path("SALUS_KERNEL_V0_1.md").exists()
    assert Path("backend/core/kernel.py").exists()
    assert Path("backend/routes/kernel.py").exists()
    assert kernel_status()["status"] == "ok"
    assert kernel_architecture()["status"] == "ok"
