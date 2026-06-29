from __future__ import annotations

import os

from fastapi import APIRouter, Header, HTTPException, Request

from backend.directorates.investor_intelligence.service import InvestorIntelligenceService


router = APIRouter(prefix="/investor-intelligence", tags=["investor-intelligence"])
service = InvestorIntelligenceService()
SALUS_PASSPHRASE = os.getenv("SALUS_PASSPHRASE", "salus-secure")


def _verify_passphrase(x_salus_passphrase: str | None):
    if x_salus_passphrase != SALUS_PASSPHRASE:
        raise HTTPException(status_code=401, detail="Unauthorized access denied")


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
):
    _verify_passphrase(x_salus_passphrase)
    payload = await request.json()
    if not isinstance(payload, dict):
        payload = {}
    return service.analyze(payload)
