from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import json


KNOWLEDGE_STORE_PATH = Path("runtime/knowledge_items.json")


VALID_CONFIDENCE = {"low", "medium", "high", "verified"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_store() -> None:
    KNOWLEDGE_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not KNOWLEDGE_STORE_PATH.exists():
        KNOWLEDGE_STORE_PATH.write_text("[]")


def load_knowledge_items() -> list[dict[str, Any]]:
    _ensure_store()
    try:
        data = json.loads(KNOWLEDGE_STORE_PATH.read_text())
    except json.JSONDecodeError:
        data = []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def save_knowledge_items(items: list[dict[str, Any]]) -> None:
    _ensure_store()
    KNOWLEDGE_STORE_PATH.write_text(json.dumps(items, indent=2, sort_keys=True))


def normalize_knowledge_item(payload: dict[str, Any]) -> dict[str, Any]:
    now = _now_iso()

    title = str(payload.get("title", "")).strip()
    domain = str(payload.get("domain", "general")).strip() or "general"
    source = str(payload.get("source", "manual")).strip() or "manual"
    summary = str(payload.get("summary", "")).strip()
    content = str(payload.get("content", "")).strip()
    confidence = str(payload.get("confidence", "medium")).strip().lower()

    if confidence not in VALID_CONFIDENCE:
        confidence = "medium"

    raw_tags = payload.get("tags", [])
    if isinstance(raw_tags, str):
        tags = [tag.strip() for tag in raw_tags.split(",") if tag.strip()]
    elif isinstance(raw_tags, list):
        tags = [str(tag).strip() for tag in raw_tags if str(tag).strip()]
    else:
        tags = []

    if not title:
        raise ValueError("title is required")

    if not summary and not content:
        raise ValueError("summary or content is required")

    return {
        "id": str(payload.get("id") or uuid4()),
        "title": title,
        "domain": domain,
        "source": source,
        "summary": summary,
        "content": content,
        "confidence": confidence,
        "tags": tags,
        "created_at": str(payload.get("created_at") or now),
        "updated_at": now,
    }


def create_knowledge_item(payload: dict[str, Any]) -> dict[str, Any]:
    item = normalize_knowledge_item(payload)
    items = load_knowledge_items()

    existing_ids = {existing.get("id") for existing in items}
    if item["id"] in existing_ids:
        raise ValueError("knowledge item id already exists")

    items.append(item)
    save_knowledge_items(items)
    return item


def list_knowledge_items(
    domain: str | None = None,
    query: str | None = None,
    tag: str | None = None,
) -> list[dict[str, Any]]:
    items = load_knowledge_items()

    if domain:
        domain_value = domain.strip().lower()
        items = [item for item in items if str(item.get("domain", "")).lower() == domain_value]

    if tag:
        tag_value = tag.strip().lower()
        items = [
            item for item in items
            if tag_value in [str(existing_tag).lower() for existing_tag in item.get("tags", [])]
        ]

    if query:
        q = query.strip().lower()
        items = [
            item for item in items
            if q in " ".join([
                str(item.get("title", "")),
                str(item.get("domain", "")),
                str(item.get("summary", "")),
                str(item.get("content", "")),
                " ".join(str(tag) for tag in item.get("tags", [])),
            ]).lower()
        ]

    return items


def get_knowledge_item(item_id: str) -> dict[str, Any] | None:
    for item in load_knowledge_items():
        if item.get("id") == item_id:
            return item
    return None


def knowledge_status() -> dict[str, Any]:
    items = load_knowledge_items()
    domains = sorted({str(item.get("domain", "general")) for item in items})
    tags = sorted({str(tag) for item in items for tag in item.get("tags", [])})

    return {
        "status": "ok",
        "module": "knowledge_engine",
        "item_count": len(items),
        "domains": domains,
        "tags": tags,
        "store": str(KNOWLEDGE_STORE_PATH),
        "next_action": "Capture high-value knowledge items that improve judgment.",
    }
