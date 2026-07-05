from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend.core.intent_classifier import classify_intent
from backend.core.subsystem_registry import route_for_intent
try:
    from backend.services.core_identity_service import core_identity_status
except Exception:  # pragma: no cover
    core_identity_status = None

try:
    from backend.services.salus_memory_service import memory_status
except Exception:  # pragma: no cover
    memory_status = None

try:
    from backend.services.knowledge_service import knowledge_status
except Exception:  # pragma: no cover
    knowledge_status = None

try:
    from backend.services.judgment_engine_service import judgment_status
except Exception:  # pragma: no cover
    judgment_status = None


CONTEXT_PACKET_VERSION = "0.3.0"


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_status(name: str, provider: Any) -> dict[str, Any]:
    if provider is None:
        return {
            "status": "unavailable",
            "module": name,
            "error": "provider not available",
        }

    try:
        return provider()
    except Exception as exc:
        return {
            "status": "error",
            "module": name,
            "error": str(exc),
        }


def build_context_packet(payload: dict[str, Any]) -> dict[str, Any]:
    user = str(payload.get("user", "Kyle")).strip() or "Kyle"
    input_text = str(payload.get("input", "")).strip()

    if not input_text:
        raise ValueError("input is required")

    classification = classify_intent(input_text)
    selected_subsystem = route_for_intent(classification["intent"])

    return {
        "status": "ok",
        "module": "context_packet",
        "version": CONTEXT_PACKET_VERSION,
        "user": user,
        "input": input_text,
        "classification": classification,
        "selected_subsystem": selected_subsystem,
        "identity": _safe_status("core_identity", core_identity_status),
        "memory": _safe_status("memory_engine", memory_status),
        "knowledge": _safe_status("knowledge_engine", knowledge_status),
        "judgment": _safe_status("judgment_engine", judgment_status),
        "operating_rules": [
            "Distinguish fact, inference, forecast, and speculation.",
            "Preserve human accountability.",
            "Use evidence and confidence levels.",
            "Prefer capability growth over dependency.",
            "Require approval before irreversible execution.",
        ],
        "timestamp": _now_iso(),
    }


def context_packet_status() -> dict[str, Any]:
    return {
        "status": "ok",
        "module": "context_packet",
        "version": CONTEXT_PACKET_VERSION,
        "inputs_required": ["input"],
        "inputs_optional": ["user"],
        "included_context": [
            "classification",
            "selected_subsystem",
            "identity",
            "memory",
            "knowledge",
            "judgment",
            "operating_rules",
        ],
    }
