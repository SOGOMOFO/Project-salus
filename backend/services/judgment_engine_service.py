from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import json


JUDGMENT_STORE_PATH = Path("runtime/judgment_items.json")

VALID_RECOMMENDATIONS = {"pursue", "pause", "delegate", "discard"}
VALID_CONFIDENCE = {"low", "medium", "high", "verified"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_store() -> None:
    JUDGMENT_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not JUDGMENT_STORE_PATH.exists():
        JUDGMENT_STORE_PATH.write_text("[]")


def load_judgment_items() -> list[dict[str, Any]]:
    _ensure_store()
    try:
        data = json.loads(JUDGMENT_STORE_PATH.read_text())
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def save_judgment_items(items: list[dict[str, Any]]) -> None:
    _ensure_store()
    JUDGMENT_STORE_PATH.write_text(json.dumps(items, indent=2, sort_keys=True))


def _normalize_list(value: Any) -> list[str]:
    if isinstance(value, str):
        return [item.strip() for item in value.split(",") if item.strip()]
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return []


def score_judgment(payload: dict[str, Any]) -> dict[str, Any]:
    evidence = _normalize_list(payload.get("evidence", []))
    risks = _normalize_list(payload.get("risks", []))
    options = _normalize_list(payload.get("options", []))
    next_action = str(payload.get("next_action", "")).strip()
    recommendation = str(payload.get("recommendation", "pause")).strip().lower()
    confidence = str(payload.get("confidence", "medium")).strip().lower()

    if recommendation not in VALID_RECOMMENDATIONS:
        recommendation = "pause"

    if confidence not in VALID_CONFIDENCE:
        confidence = "medium"

    score = 50

    score += min(len(evidence) * 8, 24)
    score += min(len(options) * 5, 15)
    score -= min(len(risks) * 5, 20)

    if next_action:
        score += 10

    if confidence == "high":
        score += 8
    elif confidence == "verified":
        score += 12
    elif confidence == "low":
        score -= 8

    if recommendation == "pursue":
        score += 5
    elif recommendation == "discard":
        score -= 5

    score = max(0, min(100, score))

    if score >= 80:
        readiness = "strong"
    elif score >= 60:
        readiness = "moderate"
    elif score >= 40:
        readiness = "weak"
    else:
        readiness = "poor"

    return {
        "score": score,
        "readiness": readiness,
        "evidence_count": len(evidence),
        "risk_count": len(risks),
        "option_count": len(options),
    }


def normalize_judgment_item(payload: dict[str, Any]) -> dict[str, Any]:
    now = _now_iso()

    decision = str(payload.get("decision", "")).strip()
    context = str(payload.get("context", "")).strip()
    recommendation = str(payload.get("recommendation", "pause")).strip().lower()
    confidence = str(payload.get("confidence", "medium")).strip().lower()

    if recommendation not in VALID_RECOMMENDATIONS:
        recommendation = "pause"

    if confidence not in VALID_CONFIDENCE:
        confidence = "medium"

    if not decision:
        raise ValueError("decision is required")

    if not context:
        raise ValueError("context is required")

    item = {
        "id": str(payload.get("id") or uuid4()),
        "decision": decision,
        "context": context,
        "options": _normalize_list(payload.get("options", [])),
        "evidence": _normalize_list(payload.get("evidence", [])),
        "risks": _normalize_list(payload.get("risks", [])),
        "confidence": confidence,
        "recommendation": recommendation,
        "next_action": str(payload.get("next_action", "")).strip(),
        "created_at": str(payload.get("created_at") or now),
        "updated_at": now,
    }

    item["judgment_score"] = score_judgment(item)

    return item


def create_judgment_item(payload: dict[str, Any]) -> dict[str, Any]:
    item = normalize_judgment_item(payload)
    items = load_judgment_items()

    if item["id"] in {existing.get("id") for existing in items}:
        raise ValueError("judgment item id already exists")

    items.append(item)
    save_judgment_items(items)
    return item


def list_judgment_items(query: str | None = None, recommendation: str | None = None) -> list[dict[str, Any]]:
    items = load_judgment_items()

    if recommendation:
        value = recommendation.strip().lower()
        items = [item for item in items if str(item.get("recommendation", "")).lower() == value]

    if query:
        q = query.strip().lower()
        items = [
            item for item in items
            if q in " ".join([
                str(item.get("decision", "")),
                str(item.get("context", "")),
                str(item.get("next_action", "")),
                " ".join(str(option) for option in item.get("options", [])),
                " ".join(str(evidence) for evidence in item.get("evidence", [])),
                " ".join(str(risk) for risk in item.get("risks", [])),
            ]).lower()
        ]

    return sorted(
        items,
        key=lambda item: int(item.get("judgment_score", {}).get("score", 0)),
        reverse=True,
    )


def get_judgment_item(item_id: str) -> dict[str, Any] | None:
    for item in load_judgment_items():
        if item.get("id") == item_id:
            return item
    return None


def judgment_status() -> dict[str, Any]:
    items = load_judgment_items()

    by_recommendation = {}
    for recommendation in VALID_RECOMMENDATIONS:
        by_recommendation[recommendation] = len([
            item for item in items
            if item.get("recommendation") == recommendation
        ])

    average_score = 0
    if items:
        average_score = round(
            sum(int(item.get("judgment_score", {}).get("score", 0)) for item in items) / len(items),
            2,
        )

    return {
        "status": "ok",
        "module": "judgment_engine",
        "item_count": len(items),
        "average_score": average_score,
        "by_recommendation": by_recommendation,
        "store": str(JUDGMENT_STORE_PATH),
        "next_action": "Capture important decisions with evidence, risks, confidence, and next action.",
    }
