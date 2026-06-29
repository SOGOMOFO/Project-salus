from __future__ import annotations

from datetime import datetime, timezone
from statistics import mean
from typing import Any, Callable, Optional


_CONFIDENCE_LEVELS = (99, 95, 90, 80, 70, 60)
_RECOMMENDATIONS = {"Pursue", "Pause", "Delegate", "Discard", "Monitor"}
_EVIDENCE_GRADES = ("A+", "A", "B", "C", "D")


def _normalize_score(value: Any, *, default: float = 50.0) -> float:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = float(default)
    return max(0.0, min(100.0, numeric))


def _confidence_band(score: float) -> int | str:
    if score >= 98:
        return 99
    if score >= 94:
        return 95
    if score >= 89:
        return 90
    if score >= 79:
        return 80
    if score >= 69:
        return 70
    if score >= 59:
        return 60
    return "below_60"


def _default_memory_writer(record: dict[str, Any]) -> None:
    from backend.memory.memory_engine import add_memory

    add_memory(
        memory_type="mission",
        title=f"Intelligence decision: {record.get('recommendation', 'Monitor')}",
        content=str(record),
        tags=["intelligence", "decision"],
        source="intelligence-core-v1",
    )


def _default_audit_logger(record: dict[str, Any]) -> None:
    try:
        from backend.security.core import security_core
    except Exception:
        return

    append_audit = getattr(security_core, "_append_audit", None)
    if not callable(append_audit):
        return

    append_audit(
        action="intelligence.evaluate",
        allowed=True,
        detail="intelligence decision evaluated",
        principal=str(record.get("actor", "intelligence-core")),
        role=str(record.get("role", "agent")),
    )


def score_evidence(evidence: Any) -> dict[str, Any]:
    base_score = 50.0
    signals: list[float] = []

    if isinstance(evidence, dict):
        for key in ("credibility", "coverage", "freshness", "consistency"):
            signals.append(_normalize_score(evidence.get(key), default=base_score))
    elif isinstance(evidence, list):
        signals = [_normalize_score(item, default=base_score) for item in evidence]
    elif isinstance(evidence, str):
        length_score = min(100.0, max(30.0, len(evidence.strip()) / 10.0))
        signals.append(length_score)
    else:
        signals.append(base_score)

    score = _normalize_score(mean(signals) if signals else base_score)
    if score >= 95:
        grade = "A+"
    elif score >= 88:
        grade = "A"
    elif score >= 75:
        grade = "B"
    elif score >= 60:
        grade = "C"
    else:
        grade = "D"

    return {
        "score": round(score, 2),
        "grade": grade,
        "confidence": _confidence_band(score),
    }


def generate_recommendation(
    *,
    strategic_fit: float,
    evidence_quality: float,
    roi: float,
    difficulty: float,
    risk: float,
    opportunity_cost: float,
    timeline: float,
) -> dict[str, Any]:
    weighted_score = (
        (0.25 * strategic_fit)
        + (0.20 * evidence_quality)
        + (0.20 * roi)
        + (0.10 * timeline)
        - (0.10 * difficulty)
        - (0.10 * risk)
        - (0.05 * opportunity_cost)
    )
    weighted_score = _normalize_score(weighted_score)

    if risk >= 85 and evidence_quality < 80:
        recommendation = "Discard"
    elif weighted_score >= 80:
        recommendation = "Pursue"
    elif weighted_score >= 65:
        recommendation = "Delegate"
    elif weighted_score >= 50:
        recommendation = "Monitor"
    elif weighted_score >= 35:
        recommendation = "Pause"
    else:
        recommendation = "Discard"

    return {
        "recommendation": recommendation,
        "score": round(weighted_score, 2),
        "confidence": _confidence_band(weighted_score),
    }


def reconcile_agent_outputs(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    if not outputs:
        return {
            "status": "ok",
            "consensus": "Monitor",
            "confidence": "below_60",
            "summary": [],
            "counts": {},
        }

    counts: dict[str, int] = {}
    confidences: list[float] = []
    summary: list[dict[str, Any]] = []
    for row in outputs:
        recommendation = str(row.get("recommendation", "Monitor")).strip().title()
        if recommendation not in _RECOMMENDATIONS:
            recommendation = "Monitor"
        counts[recommendation] = counts.get(recommendation, 0) + 1
        confidences.append(_normalize_score(row.get("confidence", 60.0), default=60.0))
        summary.append(
            {
                "agent": str(row.get("agent", "unknown")),
                "recommendation": recommendation,
                "confidence": _confidence_band(confidences[-1]),
            }
        )

    consensus = max(counts, key=counts.get)
    avg_confidence = _normalize_score(mean(confidences), default=60.0)
    return {
        "status": "ok",
        "consensus": consensus,
        "confidence": _confidence_band(avg_confidence),
        "summary": summary,
        "counts": counts,
    }


def create_decision_record(payload: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat()
    return {
        "decision_id": str(payload.get("decision_id") or f"decision-{int(datetime.now(timezone.utc).timestamp())}"),
        "timestamp": now,
        "actor": str(payload.get("actor", "intelligence-core")),
        "role": str(payload.get("role", "agent")),
        "topic": str(payload.get("topic", "general")),
        "decision_scoring": {
            "strategic_fit": _normalize_score(payload.get("strategic_fit")),
            "evidence_quality": _normalize_score(payload.get("evidence_quality")),
            "roi": _normalize_score(payload.get("roi")),
            "difficulty": _normalize_score(payload.get("difficulty")),
            "risk": _normalize_score(payload.get("risk")),
            "opportunity_cost": _normalize_score(payload.get("opportunity_cost")),
            "timeline": _normalize_score(payload.get("timeline")),
            "recommendation": str(payload.get("recommendation", "Monitor")),
            "confidence": payload.get("confidence", "below_60"),
        },
    }


def evaluate_decision(
    payload: dict[str, Any],
    *,
    memory_writer: Optional[Callable[[dict[str, Any]], None]] = None,
    audit_logger: Optional[Callable[[dict[str, Any]], None]] = None,
) -> dict[str, Any]:
    evidence = score_evidence(payload.get("evidence"))
    recommendation = generate_recommendation(
        strategic_fit=_normalize_score(payload.get("strategic_fit")),
        evidence_quality=_normalize_score(payload.get("evidence_quality", evidence["score"]), default=evidence["score"]),
        roi=_normalize_score(payload.get("roi")),
        difficulty=_normalize_score(payload.get("difficulty")),
        risk=_normalize_score(payload.get("risk")),
        opportunity_cost=_normalize_score(payload.get("opportunity_cost")),
        timeline=_normalize_score(payload.get("timeline")),
    )

    record_payload = dict(payload)
    record_payload["evidence_quality"] = _normalize_score(record_payload.get("evidence_quality", evidence["score"]))
    record_payload["recommendation"] = recommendation["recommendation"]
    record_payload["confidence"] = recommendation["confidence"]
    record = create_decision_record(record_payload)
    record["evidence"] = evidence
    record["overall"] = recommendation

    writer = memory_writer if callable(memory_writer) else _default_memory_writer
    try:
        writer(record)
    except Exception:
        pass

    logger = audit_logger if callable(audit_logger) else _default_audit_logger
    try:
        logger(record)
    except Exception:
        pass

    return record
