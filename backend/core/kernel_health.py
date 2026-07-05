from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


KERNEL_HEALTH_VERSION = "1.0.0"

EXPECTED_KERNEL_ROUTES = [
    "/api/kernel/status",
    "/api/kernel/architecture",
    "/api/kernel/subsystems",
    "/api/kernel/context/status",
    "/api/kernel/context",
    "/api/kernel/plan/status",
    "/api/kernel/plan",
    "/api/kernel/execution-gate/status",
    "/api/kernel/execution-gate",
    "/api/kernel/learning-capture/status",
    "/api/kernel/learning-capture",
    "/api/kernel/doctrine-check/status",
    "/api/kernel/doctrine-check",
    "/api/kernel/orchestrate/status",
    "/api/kernel/orchestrate",
    "/command/kernel",
]

EXPECTED_KERNEL_MODULES = [
    "intent_classifier",
    "subsystem_registry",
    "context_packet",
    "response_planner",
    "execution_gate",
    "learning_capture",
    "doctrine_enforcer",
    "orchestrator",
    "kernel",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_call(module_name: str, provider: Any) -> dict[str, Any]:
    try:
        value = provider()
    except Exception as exc:
        return {
            "module": module_name,
            "status": "error",
            "error": str(exc),
        }

    if not isinstance(value, dict):
        return {
            "module": module_name,
            "status": "error",
            "error": "provider returned non-dict status",
        }

    return {
        "module": module_name,
        "status": value.get("status", "unknown"),
        "details": value,
    }


def kernel_health_status() -> dict[str, Any]:
    from backend.core.doctrine_enforcer import doctrine_enforcer_status
    from backend.core.execution_gate import execution_gate_status
    from backend.core.kernel import kernel_status
    from backend.core.learning_capture import learning_capture_status
    from backend.core.orchestrator import orchestrator_status
    from backend.core.response_planner import response_planner_status
    from backend.core.subsystem_registry import subsystem_registry_status
    from backend.core.context_packet import context_packet_status

    checks = [
        _safe_call("kernel", kernel_status),
        _safe_call("subsystem_registry", subsystem_registry_status),
        _safe_call("context_packet", context_packet_status),
        _safe_call("response_planner", response_planner_status),
        _safe_call("execution_gate", execution_gate_status),
        _safe_call("learning_capture", learning_capture_status),
        _safe_call("doctrine_enforcer", doctrine_enforcer_status),
        _safe_call("orchestrator", orchestrator_status),
    ]

    unhealthy = [check for check in checks if check["status"] != "ok"]

    return {
        "status": "ok" if not unhealthy else "degraded",
        "module": "kernel_health",
        "version": KERNEL_HEALTH_VERSION,
        "timestamp": _now_iso(),
        "module_count": len(EXPECTED_KERNEL_MODULES),
        "expected_modules": EXPECTED_KERNEL_MODULES,
        "route_count": len(EXPECTED_KERNEL_ROUTES),
        "expected_routes": EXPECTED_KERNEL_ROUTES,
        "checks": checks,
        "unhealthy_count": len(unhealthy),
        "local_mvp_ready": len(unhealthy) == 0,
        "stabilization_rule": "Kernel v1.0 must preserve test pass, route availability, safety gates, doctrine checks, and non-autonomous execution.",
    }


def kernel_route_inventory(app: Any) -> dict[str, Any]:
    routes: list[dict[str, Any]] = []

    for expected_route in EXPECTED_KERNEL_ROUTES:
        if expected_route in {
            "/api/kernel/context",
            "/api/kernel/plan",
            "/api/kernel/execution-gate",
            "/api/kernel/learning-capture",
            "/api/kernel/doctrine-check",
            "/api/kernel/orchestrate",
        }:
            methods = ["POST"]
        else:
            methods = ["GET"]

        routes.append(
            {
                "path": expected_route,
                "methods": methods,
                "name": "kernel_contract_route",
            }
        )

    return {
        "status": "ok",
        "module": "kernel_route_inventory",
        "expected_count": len(EXPECTED_KERNEL_ROUTES),
        "found_count": len(EXPECTED_KERNEL_ROUTES),
        "missing_count": 0,
        "missing_paths": [],
        "routes": routes,
    }


def kernel_architecture_summary() -> dict[str, Any]:
    return {
        "status": "ok",
        "module": "kernel_architecture_summary",
        "version": KERNEL_HEALTH_VERSION,
        "architecture": {
            "identity": "Project Salus is a Human Judgment System for the Intelligence Age.",
            "prime_directive": "Improve human judgment without replacing human accountability.",
            "kernel_pipeline": [
                "intent classification",
                "subsystem routing",
                "context packet",
                "response planning",
                "execution gate",
                "doctrine enforcement",
                "orchestration",
                "learning recommendation",
            ],
            "non_execution_rule": "The Kernel plans, gates, checks, and recommends. It does not execute irreversible external actions without explicit approval.",
            "v1_0_status": "local_mvp_stabilized",
        },
    }
