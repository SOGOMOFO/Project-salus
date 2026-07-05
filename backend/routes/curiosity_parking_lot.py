from typing import List, Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.curiosity_parking_lot_service import (
    PARKING_STATUSES,
    REVIEW_CADENCES,
    build_dashboard,
    get_item,
    list_items,
    park_item,
    reset_parking_lot,
    review_item,
    update_item_status,
)


router = APIRouter(prefix="/curiosity-parking-lot", tags=["Curiosity Parking Lot"])

ParkingStatus = Literal["parked", "reviewing", "promoted_to_mission", "promoted_to_doctrine", "discarded", "archived"]
ReviewCadence = Literal["daily", "weekly", "monthly", "quarterly", "none"]


class ParkItemRequest(BaseModel):
    title: str = Field(..., min_length=1)
    summary: str = ""
    source: str = "manual"
    source_type: str = "other"
    topics: List[str] = Field(default_factory=list)
    claims: List[str] = Field(default_factory=list)
    reason_parked: str = ""
    status: ParkingStatus = "parked"
    review_cadence: ReviewCadence = "weekly"
    strategic_fit: int = Field(5, ge=0, le=10)
    evidence_strength: int = Field(3, ge=0, le=10)
    actionability: int = Field(3, ge=0, le=10)
    roi: int = Field(5, ge=0, le=10)
    urgency: int = Field(3, ge=0, le=10)
    risk: int = Field(5, ge=0, le=10)
    opportunity_cost: int = Field(5, ge=0, le=10)
    verification_needed: List[str] = Field(default_factory=list)
    promotion_path: str = "undecided"
    review_notes: List[str] = Field(default_factory=list)


class ParkingStatusUpdateRequest(BaseModel):
    item_id: str = Field(..., min_length=1)
    status: ParkingStatus
    review_note: str = ""


class ParkingReviewRequest(BaseModel):
    item_id: str = Field(..., min_length=1)
    evidence_strength: int = Field(5, ge=0, le=10)
    actionability: int = Field(5, ge=0, le=10)
    strategic_fit: int = Field(5, ge=0, le=10)
    roi: int = Field(5, ge=0, le=10)
    review_note: str = ""
    recommended_path: Literal["mission", "doctrine", "discard", "archive", "keep_parked"] = "keep_parked"


@router.get("/framework")
def framework():
    return {
        "name": "Project Salus Curiosity Parking Lot & Backlog V1",
        "purpose": "Store low-certainty, low-priority, or not-yet-actionable ideas without interrupting active missions.",
        "statuses": PARKING_STATUSES,
        "review_cadences": REVIEW_CADENCES,
        "core_rule": "Curiosity is not opportunity.",
    }


@router.post("/reset")
def reset():
    return reset_parking_lot()


@router.get("/dashboard")
def dashboard():
    return build_dashboard()


@router.get("/list")
def list_parking_lot_items(status: Optional[str] = None, topic: Optional[str] = None, review_cadence: Optional[str] = None):
    return list_items(status=status, topic=topic, review_cadence=review_cadence)


@router.post("/park")
def park(request: ParkItemRequest):
    return park_item(request.model_dump() if hasattr(request, "model_dump") else request.dict())


@router.post("/update-status")
def update_status(request: ParkingStatusUpdateRequest):
    return update_item_status(request.model_dump() if hasattr(request, "model_dump") else request.dict())


@router.post("/review")
def review(request: ParkingReviewRequest):
    return review_item(request.model_dump() if hasattr(request, "model_dump") else request.dict())


@router.get("/{item_id}")
def read_item(item_id: str):
    return get_item(item_id)
