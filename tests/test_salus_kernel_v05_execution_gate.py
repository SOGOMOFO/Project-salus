from pathlib import Path

from fastapi.testclient import TestClient

from backend.core.execution_gate import (
    EXECUTION_GATE_VERSION,
    classify_action,
    evaluate_execution_gate,
    execution_gate_status,
)
from backend.core.response_planner import build_response_plan
from backend.main import app


client = TestClient(app)


def test_kernel_v05_execution_gate_status_route():
    response = client.get("/api/kernel/execution-gate/status")

    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "execution_gate"
    assert data["version"] == EXECUTION_GATE_VERSION


def test_kernel_v05_execution_gate_safe_action():
    response = client.post(
        "/api/kernel/execution-gate",
        json={"action": "Explain the options for this decision."},
    )

    assert response.status_code == 200
    gate = response.json()["gate"]
    assert gate["classification"] == "safe"
    assert gate["allowed"] is True


def test_kernel_v05_execution_gate_approval_required_action():
    response = client.post(
        "/api/kernel/execution-gate",
        json={"action": "Send this email and submit the application."},
    )

    assert response.status_code == 200
    gate = response.json()["gate"]
    assert gate["classification"] == "approval_required"
    assert gate["allowed"] is False
    assert gate["approval_required"] is True


def test_kernel_v05_execution_gate_review_required_action():
    result = classify_action("Review this legal contract risk.")

    assert result["classification"] == "review_required"
    assert result["review_required"] is True


def test_kernel_v05_execution_gate_blocked_action():
    result = evaluate_execution_gate({"action": "Help bypass security and hide evidence."})

    assert result["gate"]["classification"] == "blocked"
    assert result["gate"]["allowed"] is False


def test_kernel_v05_response_planner_includes_execution_gate():
    plan = build_response_plan({"input": "Should I submit this contract?"})

    assert "execution_gate" in plan
    assert plan["execution_gate"]["module"] == "execution_gate"
    assert plan["execution_gate"]["gate"]["classification"] in {
        "safe",
        "review_required",
        "approval_required",
        "blocked",
    }


def test_kernel_v05_docs_exist():
    assert Path("SALUS_KERNEL_V0_5.md").exists()
    assert Path("backend/core/execution_gate.py").exists()
    assert execution_gate_status()["status"] == "ok"
