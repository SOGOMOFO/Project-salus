from __future__ import annotations

from fastapi import APIRouter, Header, Request

from backend.security.core import security_core


router = APIRouter(prefix="/security", tags=["security"])


@router.get("/status")
async def security_status(
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    security_core.authorize(
        action="security.status.read",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent", "readonly"},
    )
    return security_core.status()


@router.get("/audit")
async def security_audit(
    limit: int = 200,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    security_core.authorize(
        action="security.audit.read",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "readonly"},
    )
    return {"status": "ok", "audit": security_core.audit(limit=limit)}


@router.post("/lockdown")
async def security_lockdown(
    request: Request,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    context = security_core.authorize(
        action="security.lockdown.write",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander"},
    )
    payload = await request.json()
    if not isinstance(payload, dict):
        payload = {}
    enabled = bool(payload.get("enabled", False))
    return {
        "status": "updated",
        "lockdown": security_core.set_lockdown(enabled, actor=context.principal, role=context.role)["lockdown"],
    }


@router.post("/unlock")
async def security_unlock(
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    context = security_core.authorize(
        action="security.unlock.write",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander"},
    )
    return {
        "status": "updated",
        "lockdown": security_core.set_lockdown(False, actor=context.principal, role=context.role)["lockdown"],
    }
