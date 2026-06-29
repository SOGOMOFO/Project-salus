from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import HTTPException


ROLES = {"commander", "family", "agent", "readonly"}
DEFAULT_ROLE = "readonly"


@dataclass
class AuthContext:
    principal: str
    role: str
    via: str


class SecurityCore:
    def __init__(self) -> None:
        self._passphrase = os.getenv("SALUS_PASSPHRASE", "salus-secure")
        self._token_map = self._load_tokens()
        self._lockdown_enabled = str(os.getenv("SALUS_LOCKDOWN", "0")).strip() in {"1", "true", "True"}
        self._audit: list[dict[str, Any]] = []
        self._max_audit_entries = 2000
        self._plugin_permissions = self._load_plugin_permissions()

    @staticmethod
    def _load_tokens() -> dict[str, dict[str, str]]:
        raw = os.getenv("SALUS_AUTH_TOKENS", "")
        if not raw.strip():
            return {
                "salus-commander-token": {"principal": "commander-root", "role": "commander"},
                "salus-family-token": {"principal": "family-user", "role": "family"},
                "salus-agent-token": {"principal": "agent-runtime", "role": "agent"},
                "salus-readonly-token": {"principal": "observer", "role": "readonly"},
            }
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        if not isinstance(payload, dict):
            return {}

        token_map: dict[str, dict[str, str]] = {}
        for token, metadata in payload.items():
            if not isinstance(token, str) or not isinstance(metadata, dict):
                continue
            role = str(metadata.get("role", DEFAULT_ROLE)).strip().lower()
            if role not in ROLES:
                role = DEFAULT_ROLE
            token_map[token] = {
                "principal": str(metadata.get("principal", "token-user")).strip() or "token-user",
                "role": role,
            }
        return token_map

    @staticmethod
    def _load_plugin_permissions() -> dict[str, list[str]]:
        raw = os.getenv("SALUS_PLUGIN_PERMISSIONS", "")
        if not raw.strip():
            return {}
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        if not isinstance(payload, dict):
            return {}

        result: dict[str, list[str]] = {}
        for plugin, roles in payload.items():
            if not isinstance(plugin, str) or not isinstance(roles, list):
                continue
            valid_roles = [str(role).strip().lower() for role in roles if str(role).strip().lower() in ROLES]
            if valid_roles:
                result[plugin] = valid_roles
        return result

    def set_lockdown(self, enabled: bool, *, actor: str = "system", role: str = "commander") -> dict[str, Any]:
        self._lockdown_enabled = bool(enabled)
        self._append_audit(
            action="security.lockdown.update",
            allowed=True,
            detail=f"lockdown={'enabled' if enabled else 'disabled'}",
            principal=actor,
            role=role,
        )
        return {"lockdown": self._lockdown_enabled}

    def status(self) -> dict[str, Any]:
        return {
            "status": "locked" if self._lockdown_enabled else "normal",
            "zero_trust": True,
            "auth": {
                "passphrase_compatibility": True,
                "token_auth": True,
                "roles": sorted(ROLES),
            },
            "lockdown": self._lockdown_enabled,
            "audit_entries": len(self._audit),
            "plugin_permission_overrides": sorted(self._plugin_permissions.keys()),
        }

    def audit(self, limit: int = 200) -> list[dict[str, Any]]:
        safe_limit = max(1, min(int(limit), self._max_audit_entries))
        return list(self._audit[-safe_limit:])

    def reset_audit(self) -> None:
        self._audit = []

    def authorize(
        self,
        *,
        action: str,
        x_salus_passphrase: str | None,
        x_salus_token: str | None = None,
        x_salus_role: str | None = None,
        allowed_roles: Optional[set[str]] = None,
        plugin: str | None = None,
    ) -> AuthContext:
        context = self._authenticate(
            x_salus_passphrase=x_salus_passphrase,
            x_salus_token=x_salus_token,
            x_salus_role=x_salus_role,
        )

        if self._lockdown_enabled and context.role != "commander":
            self._append_audit(
                action=action,
                allowed=False,
                detail="blocked by emergency lockdown",
                principal=context.principal,
                role=context.role,
                plugin=plugin,
            )
            raise HTTPException(status_code=423, detail="Emergency lockdown active")

        required = allowed_roles or set()
        if required and context.role not in required:
            self._append_audit(
                action=action,
                allowed=False,
                detail=f"role '{context.role}' not in allowed roles",
                principal=context.principal,
                role=context.role,
                plugin=plugin,
            )
            raise HTTPException(status_code=403, detail="Insufficient role permissions")

        if plugin:
            plugin_roles = self._plugin_permissions.get(plugin)
            if plugin_roles is None:
                if action.endswith(".enable") or action.endswith(".disable"):
                    plugin_roles = ["commander"]
                elif action.endswith(".validate"):
                    plugin_roles = ["commander", "agent", "readonly", "family"]
                else:
                    plugin_roles = ["commander", "agent", "readonly", "family"]
            if context.role not in plugin_roles:
                self._append_audit(
                    action=action,
                    allowed=False,
                    detail=f"plugin '{plugin}' denied for role '{context.role}'",
                    principal=context.principal,
                    role=context.role,
                    plugin=plugin,
                )
                raise HTTPException(status_code=403, detail="Plugin permission denied")

        self._append_audit(
            action=action,
            allowed=True,
            detail="authorized",
            principal=context.principal,
            role=context.role,
            plugin=plugin,
        )
        return context

    def _authenticate(
        self,
        *,
        x_salus_passphrase: str | None,
        x_salus_token: str | None,
        x_salus_role: str | None,
    ) -> AuthContext:
        role_raw = x_salus_role if isinstance(x_salus_role, str) else ""
        normalized_role = str(role_raw or "").strip().lower() or None
        if normalized_role and normalized_role not in ROLES:
            normalized_role = DEFAULT_ROLE

        token_raw = x_salus_token if isinstance(x_salus_token, str) else ""
        token = str(token_raw or "").strip()
        if token:
            token_entry = self._token_map.get(token)
            if not token_entry:
                self._append_audit(
                    action="auth.token",
                    allowed=False,
                    detail="invalid token",
                    principal="unknown",
                    role=normalized_role or DEFAULT_ROLE,
                )
                raise HTTPException(status_code=401, detail="Unauthorized access denied")
            role = normalized_role or token_entry.get("role", DEFAULT_ROLE)
            return AuthContext(
                principal=token_entry.get("principal", "token-user"),
                role=role if role in ROLES else DEFAULT_ROLE,
                via="token",
            )

        passphrase_raw = x_salus_passphrase if isinstance(x_salus_passphrase, str) else ""
        if passphrase_raw == self._passphrase:
            return AuthContext(
                principal="passphrase-user",
                role=normalized_role or "commander",
                via="passphrase",
            )

        self._append_audit(
            action="auth.passphrase",
            allowed=False,
            detail="invalid passphrase",
            principal="unknown",
            role=normalized_role or DEFAULT_ROLE,
        )
        raise HTTPException(status_code=401, detail="Unauthorized access denied")

    def _append_audit(
        self,
        *,
        action: str,
        allowed: bool,
        detail: str,
        principal: str,
        role: str,
        plugin: str | None = None,
    ) -> None:
        row = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "action": action,
            "allowed": bool(allowed),
            "detail": detail,
            "principal": principal,
            "role": role if role in ROLES else DEFAULT_ROLE,
            "lockdown": self._lockdown_enabled,
        }
        if plugin:
            row["plugin"] = plugin
        self._audit.append(row)
        if len(self._audit) > self._max_audit_entries:
            self._audit = self._audit[-self._max_audit_entries:]


security_core = SecurityCore()
