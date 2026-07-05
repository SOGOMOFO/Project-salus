from typing import Any, Dict, List


REQUIRED_DOMAINS = [
    "ai_tool_inventory",
    "data_exposure_review",
    "acceptable_use_policy",
    "cyber_hygiene_review",
    "access_control_review",
    "vendor_ai_risk_review",
    "incident_response_readiness",
    "executive_action_plan",
]


def normalize_list(values: Any) -> List[str]:
    if not values:
        return []
    if isinstance(values, list):
        return [str(v).strip().lower() for v in values if str(v).strip()]
    return [str(values).strip().lower()]


def bool_score(value: bool, points: int) -> int:
    return points if bool(value) else 0


def assess_client_readiness(payload: Dict[str, Any]) -> Dict[str, Any]:
    ai_tools = normalize_list(payload.get("ai_tools"))
    sensitive_data_types = normalize_list(payload.get("sensitive_data_types"))
    compliance_needs = normalize_list(payload.get("compliance_needs"))

    uses_ai_tools = bool(payload.get("uses_ai_tools", False))
    business_impact = str(payload.get("business_impact_ai_failure", "low")).lower()

    score = 0
    gaps: List[str] = []
    risk_flags: List[str] = []
    recommended_deliverables: List[str] = []

    score += bool_score(payload.get("has_ai_policy", False), 15)
    score += bool_score(payload.get("has_cyber_policy", False), 10)
    score += bool_score(payload.get("mfa_enabled", False), 10)
    score += bool_score(payload.get("backups_enabled", False), 10)
    score += bool_score(payload.get("endpoint_security", False), 10)
    score += bool_score(payload.get("access_controls", False), 10)
    score += bool_score(payload.get("incident_response_plan", False), 10)
    score += bool_score(payload.get("audit_logging", False), 10)
    score += bool_score(payload.get("vendor_review_process", False), 8)
    score += bool_score(payload.get("staff_training", False), 7)

    if uses_ai_tools and not ai_tools:
        gaps.append("ai_tool_inventory_missing")
        risk_flags.append("Business uses AI but has no listed AI tool inventory.")

    if uses_ai_tools and not payload.get("has_ai_policy", False):
        gaps.append("ai_acceptable_use_policy_missing")
        recommended_deliverables.append("acceptable_use_policy")

    if sensitive_data_types:
        gaps.append("sensitive_data_exposure_review_needed")
        recommended_deliverables.append("data_exposure_review")
        risk_flags.append("Sensitive data may be exposed to AI or weak cyber controls.")

    if compliance_needs:
        gaps.append("compliance_mapping_needed")
        recommended_deliverables.append("compliance_risk_mapping")
        risk_flags.append("Compliance obligations require documentation and controls.")

    if not payload.get("mfa_enabled", False):
        gaps.append("mfa_gap")
        recommended_deliverables.append("mfa_action_plan")

    if not payload.get("backups_enabled", False):
        gaps.append("backup_resilience_gap")
        recommended_deliverables.append("backup_review")

    if not payload.get("incident_response_plan", False):
        gaps.append("incident_response_gap")
        recommended_deliverables.append("incident_response_quickstart")

    if not payload.get("audit_logging", False):
        gaps.append("audit_logging_gap")
        recommended_deliverables.append("audit_logging_review")

    if not payload.get("vendor_review_process", False):
        gaps.append("vendor_ai_risk_gap")
        recommended_deliverables.append("vendor_ai_risk_review")

    if business_impact == "high":
        score -= 10
        risk_flags.append("High business impact if AI or cyber controls fail.")
    elif business_impact == "medium":
        score -= 5

    if uses_ai_tools and sensitive_data_types and not payload.get("has_ai_policy", False):
        score -= 10
        risk_flags.append("AI usage plus sensitive data without policy creates elevated risk.")

    score = max(0, min(score, 100))
    readiness_level = classify_readiness(score)
    package = recommend_package(score, gaps, business_impact)

    recommended_deliverables = sorted(set(recommended_deliverables))

    if not recommended_deliverables:
        recommended_deliverables = ["executive_action_plan"]

    return {
        "business_name": payload.get("business_name", "Unnamed Business"),
        "industry": payload.get("industry", "general"),
        "readiness_score": score,
        "readiness_level": readiness_level,
        "recommended_package": package,
        "gaps": sorted(set(gaps)),
        "risk_flags": risk_flags,
        "recommended_deliverables": recommended_deliverables,
        "required_domains": REQUIRED_DOMAINS,
        "sales_positioning": build_sales_positioning(package),
        "next_action": build_next_action(package),
    }


def classify_readiness(score: int) -> str:
    if score >= 80:
        return "strong"
    if score >= 60:
        return "moderate"
    if score >= 35:
        return "weak"
    return "high_risk"


def recommend_package(score: int, gaps: List[str], business_impact: str) -> str:
    if score < 35 or business_impact == "high" or len(gaps) >= 6:
        return "implementation_sprint"

    if score < 70 or len(gaps) >= 3:
        return "readiness_assessment"

    return "starter_snapshot"


def build_sales_positioning(package: str) -> str:
    if package == "implementation_sprint":
        return (
            "This client needs more than a report. Position Echo Seven as a guided implementation partner "
            "to close AI, cyber, policy, and readiness gaps."
        )

    if package == "readiness_assessment":
        return (
            "This client is a fit for a structured AI Governance & Cyber Readiness Assessment with a clear "
            "risk matrix and action plan."
        )

    return (
        "This client is a fit for a low-friction starter snapshot to identify obvious AI and cyber risks."
    )


def build_next_action(package: str) -> str:
    if package == "implementation_sprint":
        return "Offer a paid implementation sprint with policies, tool inventory, access controls, and staff guidance."

    if package == "readiness_assessment":
        return "Offer the full AI Governance & Cyber Readiness Assessment."

    return "Offer a starter snapshot as the first paid engagement."
