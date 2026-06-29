from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

EventHandler = Callable[[dict[str, Any]], None]


@dataclass
class EventRecord:
    topic: str
    payload: dict[str, Any]
    timestamp: str


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[EventHandler]] = defaultdict(list)
        self._history: list[EventRecord] = []

    def subscribe(self, topic: str, handler: EventHandler) -> None:
        normalized = str(topic or "").strip().lower()
        if not normalized:
            raise ValueError("topic is required")
        self._subscribers[normalized].append(handler)

    def publish(self, topic: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        normalized = str(topic or "").strip().lower()
        if not normalized:
            raise ValueError("topic is required")

        event_payload = payload or {}
        timestamp = datetime.now(timezone.utc).isoformat()
        record = EventRecord(topic=normalized, payload=event_payload, timestamp=timestamp)
        self._history.append(record)

        listeners = self._subscribers.get(normalized, [])
        for handler in listeners:
            try:
                handler(event_payload)
            except Exception:
                # Event handlers are best-effort and should not break mission flow.
                continue

        return {
            "topic": normalized,
            "payload": event_payload,
            "timestamp": timestamp,
            "listener_count": len(listeners),
        }

    def history(self, topic: str | None = None, limit: int = 20) -> list[dict[str, Any]]:
        normalized = str(topic or "").strip().lower() if topic else None
        rows = self._history
        if normalized:
            rows = [row for row in rows if row.topic == normalized]
        limited = rows[-max(1, int(limit)):]
        return [
            {
                "topic": row.topic,
                "payload": row.payload,
                "timestamp": row.timestamp,
            }
            for row in limited
        ]

    def metrics(self) -> dict[str, Any]:
        topic_counts: dict[str, int] = defaultdict(int)
        for row in self._history:
            topic_counts[row.topic] += 1
        return {
            "subscribers": {topic: len(handlers) for topic, handlers in self._subscribers.items()},
            "published_events": len(self._history),
            "topics": dict(topic_counts),
        }
