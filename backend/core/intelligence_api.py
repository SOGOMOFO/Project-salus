from __future__ import annotations

from fastapi import APIRouter, Header, Request

from backend.core.intelligence_core import evaluate_decision, reconcile_agent_outputs
from backend.security.core import security_core


router = APIRouter(prefix="/intelligence", tags=["intelligence-core-v1"])


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


@router.get("/status")
async def intelligence_status(
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    _authorize(
        action="intelligence.status.read",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent", "readonly"},
    )
    return {
        "status": "ok",
        "core": "salus-intelligence-core-v1",
        "capabilities": [
            "evaluate_decision",
            "score_evidence",
            "reconcile_agent_outputs",
            "generate_recommendation",
            "create_decision_record",
        ],
    }


@router.post("/evaluate")
async def intelligence_evaluate(
    request: Request,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    _authorize(
        action="intelligence.evaluate",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent"},
    )
    payload = await request.json()
    if not isinstance(payload, dict):
        payload = {}

    payload["role"] = str(payload.get("role") or x_salus_role or "agent")
    record = evaluate_decision(payload)
    return {"status": "ok", "decision": record}


@router.post("/reconcile")
async def intelligence_reconcile(
    request: Request,
    x_salus_passphrase: str | None = Header(default=None),
    x_salus_token: str | None = Header(default=None),
    x_salus_role: str | None = Header(default=None),
):
    _authorize(
        action="intelligence.reconcile",
        x_salus_passphrase=x_salus_passphrase,
        x_salus_token=x_salus_token,
        x_salus_role=x_salus_role,
        allowed_roles={"commander", "family", "agent"},
    )
    payload = await request.json()
    if not isinstance(payload, dict):
        payload = {}
    outputs = payload.get("outputs", [])
    if not isinstance(outputs, list):
        outputs = []
    result = reconcile_agent_outputs(outputs)
    return {"status": "ok", "reconciliation": result}
