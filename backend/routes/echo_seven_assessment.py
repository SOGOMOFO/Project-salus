from typing import List, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.services.echo_seven_assessment_service import (
    REQUIRED_DOMAINS,
    assess_client_readiness,
)


router = APIRouter(prefix="/echo-seven/assessment", tags=["Echo Seven Assessment"])


BusinessImpact = Literal["low", "medium", "high"]


class ClientReadinessRequest(BaseModel):
    business_name: str = Field(..., min_length=1)
    industry: str = "general"
    employee_count: int = Field(1, ge=1)
    uses_ai_tools: bool = False
    ai_tools: List[str] = []
    sensitive_data_types: List[str] = []
    compliance_needs: List[str] = []
    business_impact_ai_failure: BusinessImpact = "low"

    has_ai_policy: bool = False
    has_cyber_policy: bool = False
    mfa_enabled: bool = False
    backups_enabled: bool = False
    endpoint_security: bool = False
    access_controls: bool = False
    incident_response_plan: bool = False
    audit_logging: bool = False
    vendor_review_process: bool = False
    staff_training: bool = False


@router.get("/framework")
def get_echo_seven_assessment_framework():
    return {
        "name": "Echo Seven AI Governance & Cyber Readiness Assessment",
        "purpose": "Productize AI governance, cyber readiness, and practical risk reduction for small organizations.",
        "packages": [
            "starter_snapshot",
            "readiness_assessment",
            "implementation_sprint",
        ],
        "required_domains": REQUIRED_DOMAINS,
        "positioning": (
            "Help businesses use AI safely by identifying tool usage, sensitive data exposure, cyber gaps, "
            "policy needs, and practical next actions."
        ),
    }


@router.post("/client-readiness")
def client_readiness(request: ClientReadinessRequest):
    try:
        payload = request.model_dump()
    except AttributeError:
        payload = request.dict()

    return assess_client_readiness(payload)
