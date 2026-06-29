from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


class HealthMonitor:
    def __init__(self, *, name: str = "salus-core") -> None:
        self._name = name
        self._checks: dict[str, dict[str, Any]] = {}

    def record_check(self, component: str, status: str, detail: str = "") -> None:
        normalized_component = str(component or "").strip() or "unknown"
        normalized_status = str(status or "unknown").strip().lower()
        self._checks[normalized_component] = {
            "status": normalized_status,
            "detail": str(detail or ""),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

    def summary(self) -> dict[str, Any]:
        checks = self._checks.copy()
        unhealthy = [name for name, payload in checks.items() if payload.get("status") not in {"ok", "ready", "healthy"}]
        overall = "ok" if not unhealthy else "degraded"
        return {
            "name": self._name,
            "status": overall,
            "checks": checks,
            "unhealthy_components": unhealthy,
        }
