from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import json


MEMORY_STORE_PATH = Path("runtime/salus_memory_items.json")

VALID_MEMORY_TYPES = {
    "working",
    "long_term",
    "mission",
    "user",
    "knowledge",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_store() -> None:
    MEMORY_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not MEMORY_STORE_PATH.exists():
        MEMORY_STORE_PATH.write_text("[]")


def load_memory_items() -> list[dict[str, Any]]:
    _ensure_store()
    try:
        data = json.loads(MEMORY_STORE_PATH.read_text())
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    return [item for item in data if isinstance(item, dict)]


def save_memory_items(items: list[dict[str, Any]]) -> None:
    _ensure_store()
    MEMORY_STORE_PATH.write_text(json.dumps(items, indent=2, sort_keys=True))


def normalize_memory_item(payload: dict[str, Any]) -> dict[str, Any]:
    now = _now_iso()

    title = str(payload.get("title", "")).strip()
    content = str(payload.get("content", "")).strip()
    memory_type = str(payload.get("memory_type", "working")).strip().lower()
    domain = str(payload.get("domain", "general")).strip() or "general"
    source = str(payload.get("source", "manual")).strip() or "manual"
    importance = int(payload.get("importance", 3))

    if memory_type not in VALID_MEMORY_TYPES:
        memory_type = "working"

    if importance < 1:
        importance = 1
    if importance > 5:
        importance = 5

    raw_tags = payload.get("tags", [])
    if isinstance(raw_tags, str):
        tags = [tag.strip() for tag in raw_tags.split(",") if tag.strip()]
    elif isinstance(raw_tags, list):
        tags = [str(tag).strip() for tag in raw_tags if str(tag).strip()]
    else:
        tags = []

    if not title:
        raise ValueError("title is required")

    if not content:
        raise ValueError("content is required")

    return {
        "id": str(payload.get("id") or uuid4()),
        "title": title,
        "content": content,
        "memory_type": memory_type,
        "domain": domain,
        "source": source,
        "importance": importance,
        "tags": tags,
        "created_at": str(payload.get("created_at") or now),
        "updated_at": now,
    }


def create_memory_item(payload: dict[str, Any]) -> dict[str, Any]:
    item = normalize_memory_item(payload)
    items = load_memory_items()

    if item["id"] in {existing.get("id") for existing in items}:
        raise ValueError("memory item id already exists")

    items.append(item)
    save_memory_items(items)
    return item


def list_memory_items(
    memory_type: str | None = None,
    domain: str | None = None,
    query: str | None = None,
    tag: str | None = None,
) -> list[dict[str, Any]]:
    items = load_memory_items()

    if memory_type:
        value = memory_type.strip().lower()
        items = [item for item in items if str(item.get("memory_type", "")).lower() == value]

    if domain:
        value = domain.strip().lower()
        items = [item for item in items if str(item.get("domain", "")).lower() == value]

    if tag:
        value = tag.strip().lower()
        items = [
            item for item in items
            if value in [str(existing_tag).lower() for existing_tag in item.get("tags", [])]
        ]

    if query:
        q = query.strip().lower()
        items = [
            item for item in items
            if q in " ".join([
                str(item.get("title", "")),
                str(item.get("content", "")),
                str(item.get("memory_type", "")),
                str(item.get("domain", "")),
                " ".join(str(existing_tag) for existing_tag in item.get("tags", [])),
            ]).lower()
        ]

    return sorted(items, key=lambda item: int(item.get("importance", 3)), reverse=True)


def get_memory_item(item_id: str) -> dict[str, Any] | None:
    for item in load_memory_items():
        if item.get("id") == item_id:
            return item
    return None


def memory_status() -> dict[str, Any]:
    items = load_memory_items()

    by_type = {}
    for memory_type in VALID_MEMORY_TYPES:
        by_type[memory_type] = len([
            item for item in items
            if item.get("memory_type") == memory_type
        ])

    return {
        "status": "ok",
        "module": "memory_engine",
        "item_count": len(items),
        "by_type": by_type,
        "store": str(MEMORY_STORE_PATH),
        "next_action": "Capture mission-critical memories that improve continuity and judgment.",
    }
