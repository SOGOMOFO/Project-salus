from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.core.intelligence_core import generate_judgment
from backend.core.explainability_engine import explain_recommendation


router = APIRouter()


class JudgmentRequest(BaseModel):
    strategic_fit: float = Field(default=50, ge=0, le=100)
    evidence_quality: float = Field(default=50, ge=0, le=100)
    roi: float = Field(default=50, ge=0, le=100)
    difficulty: float = Field(default=50, ge=0, le=100)
    timeline: float = Field(default=50, ge=0, le=100)
    risks: dict[str, Any] = Field(default_factory=dict)


@router.get("/")
async def home():
    return {
        "project": "Project Salus",
        "status": "Operational",
        "module": "Mission Control",
        "version": "1.0.0",
    }


@router.get("/health")
async def health():
    return {"status": "healthy"}


@router.get("/missions")
async def missions():
    return {"missions": []}


@router.post("/judgment")
async def judgment(request: JudgmentRequest):
    judgment_result = generate_judgment(
        strategic_fit=request.strategic_fit,
        evidence_quality=request.evidence_quality,
        roi=request.roi,
        difficulty=request.difficulty,
        timeline=request.timeline,
        risks=request.risks,
    )

    explanation = explain_recommendation(judgment_result)

    return {
        "status": "ok",
        "judgment": judgment_result,
        "explanation": explanation,
    }
