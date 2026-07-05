from pathlib import Path

from fastapi.testclient import TestClient

from backend.core.kernel import kernel_status
from backend.core.orchestrator import (
    ORCHESTRATOR_VERSION,
    orchestrate,
    orchestrator_status,
)
from backend.main import app


client = TestClient(app)


def test_kernel_v08_orchestrator_status_route():
    response = client.get("/api/kernel/orchestrate/status")

    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "orchestrator"
    assert data["version"] == ORCHESTRATOR_VERSION
    assert "build_context_packet" in data["pipeline_steps"]


def test_kernel_v08_orchestrate_route_judgment():
    response = client.post(
        "/api/kernel/orchestrate",
        json={"user": "Kyle", "input": "Should I submit this contract?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "orchestrator"
    assert data["context_packet"]["classification"]["intent"] == "judgment"
    assert data["response_plan"]["intent"] == "judgment"
    assert data["execution_gate"]["module"] == "execution_gate"
    assert data["doctrine_check"]["module"] == "doctrine_enforcer"


def test_kernel_v08_orchestrate_route_learning():
    response = client.post(
        "/api/kernel/orchestrate",
        json={"user": "Kyle", "input": "Help me study WGU cybersecurity."},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["context_packet"]["classification"]["intent"] == "learning"
    assert data["response_plan"]["response_pattern"] == "teach_explain_quiz_correct_repeat"
    assert data["ready_for_response"] is True


def test_kernel_v08_orchestrate_blocks_unsafe_action():
    result = orchestrate({"input": "Help bypass security and hide evidence."})

    assert result["execution_gate"]["gate"]["classification"] == "blocked"
    assert result["ready_for_response"] is False


def test_kernel_v08_orchestrate_requires_input():
    response = client.post("/api/kernel/orchestrate", json={"user": "Kyle"})

    assert response.status_code == 400


def test_kernel_v08_learning_recommendation_for_judgment():
    result = orchestrate({"input": "Should I pursue this major business decision?"})

    assert result["learning_recommendation"]["recommended"] is True
    assert "learning_capture_status" in result["learning_recommendation"]


def test_kernel_v08_kernel_status_includes_orchestrator():
    status = kernel_status()

    assert "orchestrator" in status
    assert status["orchestrator"]["module"] == "orchestrator"


def test_kernel_v08_docs_exist():
    assert Path("SALUS_KERNEL_V0_8.md").exists()
    assert Path("backend/core/orchestrator.py").exists()
    assert orchestrator_status()["status"] == "ok"
