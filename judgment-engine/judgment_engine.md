"""
Compatibility wrapper for Project Salus Judgment Engine.

The primary implementation lives in:
backend/core/intelligence_core.py
"""

from backend.core.intelligence_core import (
    score_evidence,
    generate_recommendation,
    reconcile_agent_outputs,
    create_decision_record,
    evaluate_decision,
)

__all__ = [
    "score_evidence",
    "generate_recommendation",
    "reconcile_agent_outputs",
    "create_decision_record",
    "evaluate_decision",
]