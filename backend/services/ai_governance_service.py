from typing import Any, Dict, List


SENSITIVE_DATA_TYPES = {
    "pii",
    "phi",
    "financial",
    "credentials",
    "legal",
    "medical",
    "student_records",
    "proprietary",
    "family_private",
}

REQUIRED_CONTROLS = [
    "human_approval_for_high_impact_actions",
    "audit_logging",
    "least_privilege_access",
    "kill_switch",
    "sensitive_data_rules",
    "model_fallback_plan",
    "output_verification",
]


def normalize_list(values: Any) -> List[str]:
    if not values:
        return []
    if isinstance(values, list):
        return [str(v).strip().lower() for v in values if str(v).strip()]
    return [str(values).strip().lower()]


def assess_ai_tool(payload: Dict[str, Any]) -> Dict[str, Any]:
    data_types = normalize_list(payload.get("data_types"))
    external_connections = normalize_list(payload.get("external_connections"))

    access_level = str(payload.get("access_level", "none")).lower()
    autonomy_level = str(payload.get("autonomy_level", "assistive")).lower()
    business_impact = str(payload.get("business_impact", "low")).lower()

    human_approval_required = bool(payload.get("human_approval_required", False))
    audit_logging = bool(payload.get("audit_logging", False))
    kill_switch = bool(payload.get("kill_switch", False))
    model_fallback = bool(payload.get("model_fallback", False))
    output_verification = bool(payload.get("output_verification", False))

    risk_score = 0
    missing_controls: List[str] = []
    risk_flags: List[str] = []

    if any(item in SENSITIVE_DATA_TYPES for item in data_types):
        risk_score += 20
        risk_flags.append("Sensitive data involved.")

    if access_level in {"write", "execute", "admin"}:
        risk_score += 20
        risk_flags.append("Tool has elevated access.")

    if autonomy_level in {"acts_with_approval", "acts_autonomously"}:
        risk_score += 20
        risk_flags.append("Tool can initiate or recommend operational action.")

    if autonomy_level == "acts_autonomously":
        risk_score += 20
        risk_flags.append("Autonomous action risk present.")

    if external_connections:
        risk_score += 10
        risk_flags.append("External integrations increase exposure.")

    if business_impact == "high":
        risk_score += 15
        risk_flags.append("High business impact if wrong.")
    elif business_impact == "medium":
        risk_score += 8

    if not human_approval_required and (
        autonomy_level in {"acts_with_approval", "acts_autonomously"} or business_impact == "high"
    ):
        risk_score += 20
        missing_controls.append("human_approval_for_high_impact_actions")

    if not audit_logging:
        risk_score += 10
        missing_controls.append("audit_logging")

    if not kill_switch:
        risk_score += 10
        missing_controls.append("kill_switch")

    if not model_fallback:
        risk_score += 5
        missing_controls.append("model_fallback_plan")

    if not output_verification:
        risk_score += 10
        missing_controls.append("output_verification")

    if any(item in SENSITIVE_DATA_TYPES for item in data_types):
        missing_controls.append("sensitive_data_rules")

    missing_controls = sorted(set(missing_controls))
    risk_score = min(risk_score, 100)

    if risk_score >= 70:
        risk_level = "red"
        decision = "BLOCKED_UNTIL_REMEDIATED"
    elif risk_score >= 35:
        risk_level = "amber"
        decision = "APPROVED_WITH_CONTROLS"
    else:
        risk_level = "green"
        decision = "APPROVED"

    return {
        "tool_name": payload.get("tool_name", "Unnamed AI Tool"),
        "purpose": payload.get("purpose", ""),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "decision": decision,
        "risk_flags": risk_flags,
        "missing_controls": missing_controls,
        "required_controls": REQUIRED_CONTROLS,
        "doctrine": "No powerful AI tool or agent receives unchecked authority.",
        "next_action": build_next_action(decision, missing_controls),
    }


def build_next_action(decision: str, missing_controls: List[str]) -> str:
    if decision == "APPROVED":
        return "Approve for controlled use and continue monitoring."

    if decision == "APPROVED_WITH_CONTROLS":
        return "Implement missing controls before expanded use: " + ", ".join(missing_controls)

    return "Block operational use until missing controls are implemented: " + ", ".join(missing_controls)
