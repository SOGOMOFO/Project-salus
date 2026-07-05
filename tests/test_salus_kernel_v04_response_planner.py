from pathlib import Path

from fastapi.testclient import TestClient

from backend.core.response_planner import (
    RESPONSE_PLANNER_VERSION,
    build_response_plan,
    response_planner_status,
)
from backend.main import app


client = TestClient(app)


def test_kernel_v04_plan_status_route():
    response = client.get("/api/kernel/plan/status")

    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "response_planner"
    assert data["version"] == RESPONSE_PLANNER_VERSION


def test_kernel_v04_plan_route_judgment():
    response = client.post(
        "/api/kernel/plan",
        json={"user": "Kyle", "input": "Should I pursue this business idea?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "judgment"
    assert data["approval_required"] is True
    assert data["response_pattern"] == "decision_brief_with_evidence_risk_tradeoffs"


def test_kernel_v04_plan_route_learning():
    response = client.post(
        "/api/kernel/plan",
        json={"user": "Kyle", "input": "Help me study WGU security."},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "learning"
    assert data["approval_required"] is False
    assert data["response_pattern"] == "teach_explain_quiz_correct_repeat"


def test_kernel_v04_plan_requires_input():
    response = client.post("/api/kernel/plan", json={"user": "Kyle"})

    assert response.status_code == 400


def test_kernel_v04_service_plan():
    plan = build_response_plan({"input": "Remember this for later."})

    assert plan["intent"] == "memory"
    assert plan["selected_subsystem"]["subsystem_id"] == "memory"
    assert "context_packet" in plan


def test_kernel_v04_status_service():
    status = response_planner_status()

    assert status["status"] == "ok"
    assert status["module"] == "response_planner"


def test_kernel_v04_docs_exist():
    assert Path("SALUS_KERNEL_V0_4.md").exists()
    assert Path("backend/core/response_planner.py").exists()
