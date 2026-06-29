from __future__ import annotations

from typing import Any

from backend.directorates.investor_intelligence.agent import build_expert_panel
from backend.directorates.investor_intelligence.framework import get_framework
from backend.directorates.investor_intelligence.models import AnalyzeRequest, AnalyzeResponse
from backend.directorates.investor_intelligence.portfolio import build_portfolio_model
from backend.directorates.investor_intelligence.recommendation import build_recommendation
from backend.directorates.investor_intelligence.risk import compute_risk_reward, synthesize_risks
from backend.directorates.investor_intelligence.scenarios import run_scenarios
from backend.directorates.investor_intelligence.scoring import (
    compute_composite_score,
    compute_confidence,
)
from backend.memory.memory_engine import add_memory, initialize_memory_store
from backend.memory.models import SUPPORTED_MEMORY_TYPES


DISCLAIMER = "This is decision-support analysis, not personalized financial advice."


class InvestorIntelligenceService:
    def status(self) -> dict[str, Any]:
        return {
            "status": "operational",
            "directorate": "Investor Intelligence Directorate",
            "division": "Economics & Finance",
            "decision_support_only": True,
            "brokerage_connections": "disabled",
            "expert_panel": [expert.name for expert in build_expert_panel()],
        }

    def framework(self) -> dict[str, Any]:
        payload = get_framework()
        payload["risk_policy"] = (
            "When confidence is below 80, recommendation defaults to Monitor unless risk_reward is exceptional."
        )
        payload["disclaimer"] = DISCLAIMER
        return payload

    def analyze(self, request_payload: dict[str, Any]) -> dict[str, Any]:
        request = AnalyzeRequest(**(request_payload or {}))
        scores = request.scores.model_dump()
        composite_score = compute_composite_score(scores)

        confidence = compute_confidence(
            evidence_quality=request.evidence_quality,
            has_thesis=bool(request.thesis.strip()),
            has_bear_case=bool(request.bear_case.strip()),
            has_bull_case=bool(request.bull_case.strip()),
            assumptions_count=len(request.key_assumptions),
        )
        risk_reward = compute_risk_reward(scores)

        recommendation = build_recommendation(
            composite_score=composite_score,
            confidence_band=confidence,
            exceptional_risk_reward=bool(risk_reward["exceptional"]),
            risk_score=scores["risk"],
        )
        scenario_outlook = run_scenarios(scores)
        portfolio_model = build_portfolio_model(request.portfolio_fit, scores["risk"], scores["conviction"])

        panel_summary = [expert.evaluate(scores) for expert in build_expert_panel()]
        risks = synthesize_risks(scores, request.risks)

        response = AnalyzeResponse(
            ticker_or_asset=request.ticker_or_asset,
            thesis=request.thesis or "No thesis provided.",
            bear_case=request.bear_case or "Bear case not supplied.",
            bull_case=request.bull_case or "Bull case not supplied.",
            key_assumptions=request.key_assumptions,
            evidence_quality=request.evidence_quality,
            confidence=confidence,
            scores=scores,
            risks=risks,
            portfolio_fit=request.portfolio_fit,
            recommendation=recommendation,
            disclaimer=DISCLAIMER,
            risk_reward=risk_reward,
            panel_summary=panel_summary,
            scenario_outlook=scenario_outlook,
            portfolio_model=portfolio_model,
        ).model_dump()
        response["composite_score"] = composite_score

        self._store_summary(response)
        return response

    def _store_summary(self, response: dict[str, Any]) -> None:
        memory_type = "investment" if "investment" in SUPPORTED_MEMORY_TYPES else "project"
        summary = (
            f"{response['ticker_or_asset']}: recommendation {response['recommendation']} "
            f"at confidence {response['confidence']} with composite score {response['composite_score']}."
        )
        try:
            initialize_memory_store()
            add_memory(
                memory_type=memory_type,
                title=f"Investor analysis: {response['ticker_or_asset']}",
                content=summary,
                tags=["investor-intelligence", response["recommendation"].lower()],
                source="investor-intelligence",
            )
        except Exception:
            return
