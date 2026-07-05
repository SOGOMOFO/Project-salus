from pathlib import Path

from fastapi.testclient import TestClient

from backend.core.doctrine_enforcer import (
    DOCTRINE_ENFORCER_VERSION,
    build_doctrine_check,
    check_doctrine,
    doctrine_enforcer_status,
)
from backend.core.kernel import kernel_status
from backend.core.response_planner import build_response_plan
from backend.main import app


client = TestClient(app)


def test_kernel_v07_doctrine_status_route():
    response = client.get("/api/kernel/doctrine-check/status")

    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "doctrine_enforcer"
    assert data["version"] == DOCTRINE_ENFORCER_VERSION


def test_kernel_v07_doctrine_check_route_from_input():
    response = client.post(
        "/api/kernel/doctrine-check",
        json={"user": "Kyle", "input": "Should I submit this contract?"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "doctrine_check"
    assert data["doctrine"]["module"] == "doctrine_enforcer"
    assert data["doctrine"]["total_rules"] >= 5


def test_kernel_v07_doctrine_check_complete_plan_passes():
    plan = build_response_plan({"input": "Should I make this decision?"})
    result = check_doctrine(plan)

    assert result["score"] >= 0.8
    assert result["critical_violation_count"] == 0


def test_kernel_v07_doctrine_check_incomplete_plan_flags_violations():
    result = check_doctrine({"response": "Do it."})

    assert result["compliant"] is False
    assert result["violations"]


def test_kernel_v07_doctrine_check_requires_plan_or_input():
    response = client.post("/api/kernel/doctrine-check", json={})

    assert response.status_code == 400


def test_kernel_v07_build_doctrine_check_with_plan_payload():
    result = build_doctrine_check(
        {
            "plan": {
                "response_rules": [
                    "Preserve human accountability.",
                    "State uncertainty.",
                    "Use evidence and risks.",
                    "Require approval before irreversible execution.",
                    "Support capability growth.",
                ]
            }
        }
    )

    assert result["doctrine"]["compliant"] is True


def test_kernel_v07_kernel_status_includes_doctrine_enforcer():
    status = kernel_status()

    assert "doctrine_enforcer" in status
    assert status["doctrine_enforcer"]["module"] == "doctrine_enforcer"


def test_kernel_v07_docs_exist():
    assert Path("SALUS_KERNEL_V0_7.md").exists()
    assert Path("backend/core/doctrine_enforcer.py").exists()
    assert doctrine_enforcer_status()["status"] == "ok"
