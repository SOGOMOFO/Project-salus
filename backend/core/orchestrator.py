from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend.core.doctrine_enforcer import check_doctrine
from backend.core.learning_capture import learning_capture_status
from backend.core.response_planner import build_response_plan


ORCHESTRATOR_VERSION = "0.8.0"

PIPELINE_STEPS = [
    "receive_request",
    "build_context_packet",
    "classify_intent",
    "select_subsystem",
    "build_response_plan",
    "run_execution_gate",
    "run_doctrine_check",
    "recommend_learning_capture",
    "return_orchestration_packet",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def orchestrator_status() -> dict[str, Any]:
    return {
        "status": "ok",
        "module": "orchestrator",
        "version": ORCHESTRATOR_VERSION,
        "pipeline_steps": PIPELINE_STEPS,
        "rule": "The orchestrator plans and gates responses. It does not execute external actions.",
    }


def _learning_recommendation(plan: dict[str, Any], doctrine: dict[str, Any]) -> dict[str, Any]:
    intent = str(plan.get("intent", "general"))
    gate = plan.get("execution_gate", {}).get("gate", {})
    gate_classification = gate.get("classification", "unknown")

    should_capture = intent in {"judgment", "command", "agent"} or gate_classification in {
        "approval_required",
        "blocked",
    } or not doctrine.get("compliant", False)

    if should_capture:
        reason = "Meaningful decision, gated action, or doctrine gap should be reviewed after outcome."
    else:
        reason = "Routine low-risk support. Learning capture optional."

    return {
        "recommended": should_capture,
        "reason": reason,
        "suggested_fields": [
            "input",
            "outcome",
            "lesson",
            "future_rule",
            "confidence",
            "tags",
        ],
        "learning_capture_status": learning_capture_status(),
    }


def orchestrate(payload: dict[str, Any]) -> dict[str, Any]:
    input_text = str(payload.get("input", "")).strip()

    if not input_text:
        raise ValueError("input is required")

    response_plan = build_response_plan(payload)
    doctrine_result = check_doctrine(response_plan)
    context_packet = response_plan["context_packet"]
    execution_gate = response_plan["execution_gate"]

    return {
        "status": "ok",
        "module": "orchestrator",
        "version": ORCHESTRATOR_VERSION,
        "timestamp": _now_iso(),
        "pipeline_steps": PIPELINE_STEPS,
        "input": input_text,
        "user": response_plan["context_packet"].get("user", payload.get("user", "Kyle")),
        "context_packet": context_packet,
        "response_plan": response_plan,
        "execution_gate": execution_gate,
        "doctrine_check": doctrine_result,
        "learning_recommendation": _learning_recommendation(response_plan, doctrine_result),
        "ready_for_response": _ready_for_response(execution_gate, doctrine_result),
        "required_next_step": _required_next_step(execution_gate, doctrine_result),
    }


def _ready_for_response(execution_gate: dict[str, Any], doctrine_result: dict[str, Any]) -> bool:
    gate = execution_gate.get("gate", {})
    gate_classification = gate.get("classification")

    if gate_classification == "blocked":
        return False

    if doctrine_result.get("critical_violation_count", 0) > 0:
        return False

    return True


def _required_next_step(execution_gate: dict[str, Any], doctrine_result: dict[str, Any]) -> str:
    gate = execution_gate.get("gate", {})
    gate_classification = gate.get("classification")

    if gate_classification == "blocked":
        return "Do not execute. Refuse or redirect within Salus safety boundaries."

    if gate_classification == "approval_required":
        return "Prepare response, but require explicit user approval before execution."

    if doctrine_result.get("critical_violation_count", 0) > 0:
        return "Revise plan before response. Critical doctrine violation present."

    if doctrine_result.get("violations"):
        return "Proceed carefully and note doctrine gaps or limitations."

    return "Proceed with planned response."
