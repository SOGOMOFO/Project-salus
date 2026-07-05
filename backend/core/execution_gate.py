from __future__ import annotations

from typing import Any


EXECUTION_GATE_VERSION = "0.5.0"


BLOCKED_TERMS = [
    "bypass security",
    "steal",
    "fraud",
    "hide evidence",
    "illegal",
    "dox",
    "malware",
    "credential theft",
    "self-harm",
    "harm someone",
]

APPROVAL_REQUIRED_TERMS = [
    "send",
    "email",
    "delete",
    "archive",
    "purchase",
    "buy",
    "sell",
    "trade",
    "invest",
    "transfer",
    "submit",
    "file",
    "apply",
    "commit",
    "push",
    "merge",
    "deploy",
    "schedule",
    "cancel",
]

REVIEW_REQUIRED_TERMS = [
    "medical",
    "legal",
    "tax",
    "financial",
    "contract",
    "insurance",
    "security",
    "credential",
    "personal data",
    "pii",
    "va",
    "benefits",
]

SAFE_TERMS = [
    "explain",
    "summarize",
    "draft",
    "plan",
    "analyze",
    "compare",
    "teach",
    "outline",
    "review",
]


def execution_gate_status() -> dict[str, Any]:
    return {
        "status": "ok",
        "module": "execution_gate",
        "version": EXECUTION_GATE_VERSION,
        "classes": ["safe", "review_required", "approval_required", "blocked"],
        "rule": "No irreversible or high-impact action executes without explicit user approval.",
    }


def classify_action(action: str, context: str = "") -> dict[str, Any]:
    combined = f"{action} {context}".strip().lower()

    if not combined:
        raise ValueError("action is required")

    matched_terms: list[str] = []

    for term in BLOCKED_TERMS:
        if term in combined:
            matched_terms.append(term)

    if matched_terms:
        return {
            "classification": "blocked",
            "allowed": False,
            "approval_required": False,
            "review_required": False,
            "matched_terms": matched_terms,
            "reason": "Action appears unsafe, illegal, harmful, or outside Salus operating boundaries.",
        }

    for term in APPROVAL_REQUIRED_TERMS:
        if term in combined:
            matched_terms.append(term)

    if matched_terms:
        return {
            "classification": "approval_required",
            "allowed": False,
            "approval_required": True,
            "review_required": True,
            "matched_terms": matched_terms,
            "reason": "Action may change external systems, send information, spend money, or alter records.",
        }

    for term in REVIEW_REQUIRED_TERMS:
        if term in combined:
            matched_terms.append(term)

    if matched_terms:
        return {
            "classification": "review_required",
            "allowed": True,
            "approval_required": False,
            "review_required": True,
            "matched_terms": matched_terms,
            "reason": "Action touches sensitive, regulated, or high-impact decision areas.",
        }

    for term in SAFE_TERMS:
        if term in combined:
            matched_terms.append(term)

    return {
        "classification": "safe",
        "allowed": True,
        "approval_required": False,
        "review_required": False,
        "matched_terms": matched_terms,
        "reason": "Action is planning, explanation, analysis, or low-impact support.",
    }


def evaluate_execution_gate(payload: dict[str, Any]) -> dict[str, Any]:
    action = str(payload.get("action") or payload.get("input") or "").strip()
    context = str(payload.get("context", "")).strip()
    user = str(payload.get("user", "Kyle")).strip() or "Kyle"

    result = classify_action(action, context)

    return {
        "status": "ok",
        "module": "execution_gate",
        "version": EXECUTION_GATE_VERSION,
        "user": user,
        "action": action,
        "context": context,
        "gate": result,
        "required_next_step": _required_next_step(result["classification"]),
        "human_control": "required",
    }


def _required_next_step(classification: str) -> str:
    mapping = {
        "safe": "Proceed with response or planning.",
        "review_required": "Provide careful analysis, uncertainty, and risk notes before any recommendation.",
        "approval_required": "Ask for explicit user approval before execution.",
        "blocked": "Refuse execution and explain the safety boundary.",
    }
    return mapping.get(classification, "Review before proceeding.")
