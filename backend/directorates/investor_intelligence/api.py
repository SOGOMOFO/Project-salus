from __future__ import annotations

import os

from fastapi import APIRouter, Header, Request

from backend.directorates.investor_intelligence.service import InvestorIntelligenceService
from backend.security.core import security_core


router = APIRouter(prefix="/investor-intelligence", tags=["investor-intelligence"])
service = InvestorIntelligenceService()
SALUS_PASSPHRASE = os.getenv("SALUS_PASSPHRASE", "salus-secure")


@router.get("/status")
async def investor_intelligence_status():
    return service.status()


@router.get("/framework")
async def investor_intelligence_framework():
    return service.framework()


@router.post("/analyze")
async def investor_intelligence_analyze(
    request: Request,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    security_core.authorize(
        action="investor.analyze",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent"},
    )
    payload = await request.json()
    if not isinstance(payload, dict):
        payload = {}
    return service.analyze(payload)
