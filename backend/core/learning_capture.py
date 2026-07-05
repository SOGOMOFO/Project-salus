from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import json


LEARNING_CAPTURE_VERSION = "0.6.0"
LEARNING_STORE_PATH = Path("runtime/kernel_learning_records.json")

VALID_CONFIDENCE = {"low", "medium", "high", "verified"}
VALID_OUTCOMES = {"success", "partial", "failed", "unknown"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_store() -> None:
    LEARNING_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not LEARNING_STORE_PATH.exists():
        LEARNING_STORE_PATH.write_text("[]")


def load_learning_records() -> list[dict[str, Any]]:
    _ensure_store()

    try:
        data = json.loads(LEARNING_STORE_PATH.read_text())
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    return [record for record in data if isinstance(record, dict)]


def save_learning_records(records: list[dict[str, Any]]) -> None:
    _ensure_store()
    LEARNING_STORE_PATH.write_text(json.dumps(records, indent=2, sort_keys=True))


def normalize_learning_record(payload: dict[str, Any]) -> dict[str, Any]:
    now = _now_iso()

    input_text = str(payload.get("input", "")).strip()
    outcome = str(payload.get("outcome", "unknown")).strip().lower()
    lesson = str(payload.get("lesson", "")).strip()
    future_rule = str(payload.get("future_rule", "")).strip()
    confidence = str(payload.get("confidence", "medium")).strip().lower()
    source = str(payload.get("source", "manual")).strip() or "manual"

    if outcome not in VALID_OUTCOMES:
        outcome = "unknown"

    if confidence not in VALID_CONFIDENCE:
        confidence = "medium"

    raw_tags = payload.get("tags", [])
    if isinstance(raw_tags, str):
        tags = [tag.strip() for tag in raw_tags.split(",") if tag.strip()]
    elif isinstance(raw_tags, list):
        tags = [str(tag).strip() for tag in raw_tags if str(tag).strip()]
    else:
        tags = []

    if not input_text:
        raise ValueError("input is required")

    if not lesson:
        raise ValueError("lesson is required")

    if not future_rule:
        raise ValueError("future_rule is required")

    return {
        "id": str(payload.get("id") or uuid4()),
        "input": input_text,
        "outcome": outcome,
        "lesson": lesson,
        "future_rule": future_rule,
        "confidence": confidence,
        "source": source,
        "tags": tags,
        "created_at": str(payload.get("created_at") or now),
        "updated_at": now,
    }


def capture_learning(payload: dict[str, Any]) -> dict[str, Any]:
    record = normalize_learning_record(payload)
    records = load_learning_records()

    if record["id"] in {existing.get("id") for existing in records}:
        raise ValueError("learning record id already exists")

    records.append(record)
    save_learning_records(records)
    return record


def list_learning_records(
    outcome: str | None = None,
    query: str | None = None,
    tag: str | None = None,
) -> list[dict[str, Any]]:
    records = load_learning_records()

    if outcome:
        value = outcome.strip().lower()
        records = [record for record in records if str(record.get("outcome", "")).lower() == value]

    if tag:
        value = tag.strip().lower()
        records = [
            record for record in records
            if value in [str(existing_tag).lower() for existing_tag in record.get("tags", [])]
        ]

    if query:
        q = query.strip().lower()
        records = [
            record for record in records
            if q in " ".join([
                str(record.get("input", "")),
                str(record.get("outcome", "")),
                str(record.get("lesson", "")),
                str(record.get("future_rule", "")),
                " ".join(str(existing_tag) for existing_tag in record.get("tags", [])),
            ]).lower()
        ]

    return sorted(records, key=lambda record: str(record.get("created_at", "")), reverse=True)


def get_learning_record(record_id: str) -> dict[str, Any] | None:
    for record in load_learning_records():
        if record.get("id") == record_id:
            return record
    return None


def learning_capture_status() -> dict[str, Any]:
    records = load_learning_records()

    by_outcome = {
        outcome: len([record for record in records if record.get("outcome") == outcome])
        for outcome in sorted(VALID_OUTCOMES)
    }

    return {
        "status": "ok",
        "module": "learning_capture",
        "version": LEARNING_CAPTURE_VERSION,
        "record_count": len(records),
        "by_outcome": by_outcome,
        "store": str(LEARNING_STORE_PATH),
        "next_action": "Capture lessons after meaningful actions, decisions, or outcomes.",
    }
