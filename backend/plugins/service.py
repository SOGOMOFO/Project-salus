from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from backend.forge.generator import discover_plugins, disable_plugin, enable_plugin


_REQUIRED_MANIFEST_KEYS = {
    "name": str,
    "slug": str,
    "version": str,
    "enabled": bool,
    "dependencies": list,
    "health": dict,
}


class PluginService:
    def __init__(self, project_root: Optional[Path | str] = None) -> None:
        self._project_root = Path(project_root).resolve() if project_root else None

    def discover(self) -> list[dict[str, Any]]:
        return discover_plugins(self._project_root)

    def health(self) -> dict[str, Any]:
        plugins = self.discover()
        degraded = [item["slug"] for item in plugins if item.get("health", {}).get("status") != "healthy"]
        return {
            "status": "ok" if not degraded else "degraded",
            "count": len(plugins),
            "degraded": degraded,
            "plugins": plugins,
        }

    def enable(self, slug: str) -> dict[str, Any]:
        return enable_plugin(slug, project_root=self._project_root)

    def disable(self, slug: str) -> dict[str, Any]:
        return disable_plugin(slug, project_root=self._project_root)

    def validate_manifest(self, slug: str) -> dict[str, Any]:
        plugin = next((item for item in self.discover() if item.get("slug") == slug), None)
        if not plugin:
            raise ValueError(f"Plugin '{slug}' not found")

        issues: list[str] = []
        for key, expected_type in _REQUIRED_MANIFEST_KEYS.items():
            value = plugin.get(key)
            if value is None:
                issues.append(f"missing:{key}")
                continue
            if not isinstance(value, expected_type):
                issues.append(f"invalid_type:{key}")

        return {
            "slug": slug,
            "valid": len(issues) == 0,
            "issues": issues,
        }
