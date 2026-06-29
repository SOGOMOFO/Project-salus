from __future__ import annotations

import os

from fastapi import APIRouter, Header, HTTPException, Request

from backend.forge.generator import create_directorate, discover_plugins
from backend.security.core import security_core


router = APIRouter(prefix="/forge", tags=["forge"])
SALUS_PASSPHRASE = os.getenv("SALUS_PASSPHRASE", "salus-secure")


def _authorize(
    *,
    action: str,
    x_salus_passphrase: str | None,
    x_salus_token: str | None,
    x_salus_role: str | None,
    allowed_roles: set[str],
) -> None:
    security_core.authorize(
        action=action,
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles=allowed_roles,
    )


@router.get("")
async def forge_status(
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    _authorize(
        action="forge.status.read",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent", "readonly"},
    )
    return {
        "status": "ready",
        "capabilities": [
            "directorate-generator",
            "plugin-discovery",
            "agent-generator",
            "service-generator",
            "api-generator",
            "test-generator",
            "docs-generator",
            "registry-updates",
        ],
    }


@router.get("/plugins")
async def forge_plugins(
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    _authorize(
        action="forge.plugins.read",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent", "readonly"},
    )
    return {"status": "ok", "plugins": discover_plugins()}


@router.post("/directorates/create")
async def forge_create_directorate(
    request: Request,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    _authorize(
        action="forge.directorates.create",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "agent"},
    )
    payload = await request.json()
    if not isinstance(payload, dict):
        payload = {}
    name = str(payload.get("name", "")).strip()
    overwrite = bool(payload.get("overwrite", False))
    if not name:
        raise HTTPException(status_code=400, detail="name is required")
    result = create_directorate(name=name, overwrite=overwrite)
    return {"status": "created", "result": result}
