from __future__ import annotations

import os

from fastapi import APIRouter, Header

from backend.plugins.service import PluginService
from backend.security.core import security_core


router = APIRouter(prefix="/plugins", tags=["plugins"])
service = PluginService()
SALUS_PASSPHRASE = os.getenv("SALUS_PASSPHRASE", "salus-secure")


def _authorize(
    *,
    action: str,
    x_salus_passphrase: str | None,
    x_salus_token: str | None,
    x_salus_role: str | None,
    plugin: str | None = None,
    allowed_roles: set[str] | None = None,
) -> None:
    security_core.authorize(
        action=action,
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        plugin=plugin,
        allowed_roles=allowed_roles,
    )


@router.get("")
async def list_plugins(
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    _authorize(
        action="plugins.list",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent", "readonly"},
    )
    return {"status": "ok", "plugins": service.discover()}


@router.get("/health")
async def plugin_health(
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    _authorize(
        action="plugins.health",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent", "readonly"},
    )
    return service.health()


@router.post("/{slug}/enable")
async def enable_plugin_route(
    slug: str,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    _authorize(
        action="plugins.permission.enable",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        plugin=slug,
        allowed_roles={"commander", "agent"},
    )
    result = service.enable(slug)
    return {"status": "updated", "plugin": result}


@router.post("/{slug}/disable")
async def disable_plugin_route(
    slug: str,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    _authorize(
        action="plugins.permission.disable",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        plugin=slug,
        allowed_roles={"commander", "agent"},
    )
    result = service.disable(slug)
    return {"status": "updated", "plugin": result}


@router.get("/{slug}/validate")
async def validate_plugin_manifest_route(
    slug: str,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    _authorize(
        action="plugins.permission.validate",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        plugin=slug,
        allowed_roles={"commander", "family", "agent", "readonly"},
    )
    payload = service.validate_manifest(slug)
    payload["status"] = "ok" if payload["valid"] else "invalid"
    return payload
