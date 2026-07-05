from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.wealth_os_service import (
    DOLLAR_MISSIONS,
    build_cash_allocation,
    classify_single_dollar,
)


router = APIRouter(prefix="/wealth-os", tags=["Wealth OS"])


Timeframe = Literal["immediate", "short_term", "0_12_months", "medium_term", "long_term"]
Goal = Literal[
    "security",
    "wealth_building",
    "retirement",
    "legacy",
    "human_capital",
    "business_growth",
    "speculative",
]
RiskTolerance = Literal["low", "medium", "high"]


class DollarClassificationRequest(BaseModel):
    amount: float = Field(..., ge=0)
    emergency_months: float = Field(0, ge=0)
    target_emergency_months: float = Field(6, ge=0)
    highest_debt_apr: float = Field(0, ge=0)
    timeframe: Timeframe = "long_term"
    goal: Goal = "wealth_building"
    risk_tolerance: RiskTolerance = "medium"


class CashAllocationRequest(BaseModel):
    cash_available: float = Field(..., ge=0)
    monthly_expenses: float = Field(..., ge=0)
    current_emergency_cash: float = Field(0, ge=0)
    target_emergency_months: float = Field(6, ge=0)
    upcoming_obligations_90_days: float = Field(0, ge=0)
    high_interest_debt_balance: float = Field(0, ge=0)
    human_capital_need: float = Field(0, ge=0)
    business_capital_need: float = Field(0, ge=0)
    speculative_cap_percent: float = Field(10, ge=0, le=20)


@router.get("/framework")
def get_wealth_os_framework():
    return {
        "name": "Project Salus Wealth Operating System",
        "purpose": "Assign every dollar a mission before it becomes idle or speculative.",
        "doctrine": "Security first, compounding second, speculation last.",
        "dollar_missions": DOLLAR_MISSIONS,
        "default_priority_order": [
            "security_cash",
            "operating_cash",
            "debt_attack",
            "human_capital",
            "business_capital",
            "index_investing",
            "speculative_capital",
        ],
    }


@router.post("/classify-dollar")
def classify_dollar(request: DollarClassificationRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return classify_single_dollar(payload)


@router.post("/allocate-cash")
def allocate_cash(request: CashAllocationRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return build_cash_allocation(payload)
