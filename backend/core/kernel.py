from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend.core.intent_classifier import classify_intent
from backend.core.learning_capture import learning_capture_status
from backend.core.doctrine_enforcer import doctrine_enforcer_status
from backend.core.orchestrator import orchestrator_status

from backend.core.subsystem_registry import route_for_intent, subsystem_registry_status


KERNEL_VERSION = "0.1.0"

SALUS_OS_LAYERS = [
    "command",
    "intelligence",
    "reasoning",
    "execution",
    "learning",
    "memory",
    "automation",
    "integration",
    "security",
    "interface",
]

REQUEST_FLOW = [
    "receive_input",
    "load_identity",
    "load_memory_context",
    "classify_intent",
    "select_capability",
    "apply_judgment",
    "build_plan",
    "require_approval_if_needed",
    "produce_response",
    "capture_learning",
]


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def kernel_status() -> dict[str, Any]:
    return {
        "status": "ok",
        "module": "salus_kernel",
        "version": KERNEL_VERSION,
        "identity": "Project Salus is a Human Judgment System for the Intelligence Age.",
        "prime_directive": "Improve human judgment without replacing human accountability.",
        "layer_count": len(SALUS_OS_LAYERS),
        "layers": SALUS_OS_LAYERS,
        "request_flow": REQUEST_FLOW,
        "subsystem_registry": subsystem_registry_status(),
        "learning_capture": learning_capture_status(),
        "doctrine_enforcer": doctrine_enforcer_status(),
        "orchestrator": orchestrator_status(),
        "timestamp": _now_iso(),
    }


def classify_intent(text: str) -> dict[str, Any]:
    value = text.strip().lower()

    if any(word in value for word in ["learn", "study", "school", "wgu", "psp", "teach"]):
        intent = "learning"
        layer = "learning"
    elif any(word in value for word in ["decide", "should i", "risk", "recommend", "option"]):
        intent = "judgment"
        layer = "reasoning"
    elif any(word in value for word in ["remember", "memory", "context"]):
        intent = "memory"
        layer = "memory"
    elif any(word in value for word in ["mission", "today", "priority", "execute"]):
        intent = "command"
        layer = "command"
    elif any(word in value for word in ["agent", "commander", "cyber", "finance", "teacher"]):
        intent = "agent"
        layer = "execution"
    else:
        intent = "general"
        layer = "command"

    return {
        "intent": intent,
        "layer": layer,
        "confidence": "medium",
        "input_length": len(text),
    }


def route_request(payload: dict[str, Any]) -> dict[str, Any]:
    text = str(payload.get("input", "")).strip()
    user = str(payload.get("user", "Kyle")).strip() or "Kyle"

    if not text:
        raise ValueError("input is required")

    classification = classify_intent(text)
    from backend.core.context_packet import build_context_packet

    return {
        "status": "ok",
        "kernel_version": KERNEL_VERSION,
        "user": user,
        "input": text,
        "classification": classification,
        "flow": REQUEST_FLOW,
        "approval_required": classification["intent"] in {"judgment", "agent"},
        "selected_subsystem": route_for_intent(classification["intent"]),
        "context_packet": build_context_packet({"user": user, "input": text}),
        "next_action": _next_action_for_intent(classification["intent"]),
        "timestamp": _now_iso(),
    }


def _next_action_for_intent(intent: str) -> str:
    mapping = {
        "learning": "Send request to Teaching Engine.",
        "judgment": "Send request to Judgment Engine and require human accountability.",
        "memory": "Send request to Memory Engine.",
        "command": "Send request to Command Layer.",
        "agent": "Select appropriate agent and generate planning-only response.",
        "general": "Use Core Identity, context, and available modules to respond.",
    }
    return mapping.get(intent, mapping["general"])


def kernel_architecture() -> dict[str, Any]:
    return {
        "status": "ok",
        "version": KERNEL_VERSION,
        "architecture": {
            "kernel": "central orchestrator",
            "layers": SALUS_OS_LAYERS,
            "request_flow": REQUEST_FLOW,
            "hard_rules": [
                "Human accountability remains required.",
                "Do not fabricate certainty.",
                "Separate fact, inference, forecast, and speculation.",
                "Require approval before irreversible execution.",
                "Prefer capability growth over dependency.",
            ],
        },
    }
