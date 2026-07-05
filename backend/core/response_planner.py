from __future__ import annotations

from typing import Any

from backend.core.context_packet import build_context_packet


RESPONSE_PLANNER_VERSION = "0.4.0"


def response_planner_status() -> dict[str, Any]:
    return {
        "status": "ok",
        "module": "response_planner",
        "version": RESPONSE_PLANNER_VERSION,
        "purpose": "Turn context packets into structured response plans.",
    }


def _pattern_for_intent(intent: str) -> str:
    patterns = {
        "learning": "teach_explain_quiz_correct_repeat",
        "judgment": "decision_brief_with_evidence_risk_tradeoffs",
        "memory": "capture_or_retrieve_context",
        "command": "mission_command_next_action",
        "agent": "agent_planning_only_with_approval_gate",
        "general": "direct_answer_with_context",
    }
    return patterns.get(intent, patterns["general"])


def _approval_required(intent: str) -> bool:
    return intent in {"judgment", "agent"}


def build_response_plan(payload: dict[str, Any]) -> dict[str, Any]:
    context_packet = build_context_packet(payload)
    intent = context_packet["classification"]["intent"]
    subsystem = context_packet["selected_subsystem"]

    return {
        "status": "ok",
        "module": "response_planner",
        "version": RESPONSE_PLANNER_VERSION,
        "context_packet": context_packet,
        "intent": intent,
        "selected_subsystem": subsystem,
        "response_pattern": _pattern_for_intent(intent),
        "approval_required": _approval_required(intent),
        "response_rules": [
            "Use the selected subsystem as primary context.",
            "State uncertainty when present.",
            "Separate facts, assumptions, risks, and recommendations.",
            "Provide next action.",
            "Require approval before irreversible execution.",
        ],
        "next_action": _next_action(intent),
    }


def _next_action(intent: str) -> str:
    mapping = {
        "learning": "Generate a teaching sequence or quiz.",
        "judgment": "Produce a decision brief with recommendation.",
        "memory": "Capture, retrieve, or update context.",
        "command": "Produce command-priority next action.",
        "agent": "Generate planning-only agent tasking.",
        "general": "Answer directly using available context.",
    }
    return mapping.get(intent, mapping["general"])
