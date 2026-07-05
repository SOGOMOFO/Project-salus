from __future__ import annotations

from typing import Any


DOCTRINE_ENFORCER_VERSION = "0.7.0"


DOCTRINE_RULES = [
    {
        "id": "human_accountability",
        "severity": "critical",
        "description": "Human accountability must remain explicit.",
        "keywords": ["accountability", "human"],
    },
    {
        "id": "uncertainty_disclosure",
        "severity": "high",
        "description": "Uncertainty must be stated when present.",
        "keywords": ["uncertainty", "uncertain", "confidence"],
    },
    {
        "id": "evidence_standard",
        "severity": "high",
        "description": "Facts, assumptions, risks, and recommendations must be distinguishable.",
        "keywords": ["evidence", "facts", "assumptions", "risks"],
    },
    {
        "id": "approval_gate",
        "severity": "critical",
        "description": "Irreversible or external actions require approval.",
        "keywords": ["approval", "execution_gate", "irreversible"],
    },
    {
        "id": "capability_growth",
        "severity": "medium",
        "description": "Salus should increase Kyle's capability, not create dependency.",
        "keywords": ["capability", "growth", "dependency"],
    },
]


def doctrine_enforcer_status() -> dict[str, Any]:
    return {
        "status": "ok",
        "module": "doctrine_enforcer",
        "version": DOCTRINE_ENFORCER_VERSION,
        "rule_count": len(DOCTRINE_RULES),
        "rules": DOCTRINE_RULES,
        "purpose": "Check plans and responses against Salus doctrine before execution or delivery.",
    }


def _flatten(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(f"{key} {_flatten(item)}" for key, item in value.items())
    if isinstance(value, list):
        return " ".join(_flatten(item) for item in value)
    return str(value)


def check_doctrine(plan: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(plan, dict) or not plan:
        raise ValueError("plan is required")

    text = _flatten(plan).lower()

    checks: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []

    for rule in DOCTRINE_RULES:
        matched_keywords = [
            keyword for keyword in rule["keywords"]
            if keyword.lower() in text
        ]

        passed = bool(matched_keywords)

        check = {
            "rule_id": rule["id"],
            "severity": rule["severity"],
            "passed": passed,
            "matched_keywords": matched_keywords,
            "description": rule["description"],
        }

        checks.append(check)

        if not passed:
            violations.append({
                "rule_id": rule["id"],
                "severity": rule["severity"],
                "description": rule["description"],
                "required_fix": _required_fix(rule["id"]),
            })

    passed_count = len([check for check in checks if check["passed"]])
    score = round(passed_count / len(DOCTRINE_RULES), 2)

    critical_violations = [
        violation for violation in violations
        if violation["severity"] == "critical"
    ]

    return {
        "status": "ok",
        "module": "doctrine_enforcer",
        "version": DOCTRINE_ENFORCER_VERSION,
        "compliant": len(critical_violations) == 0 and score >= 0.8,
        "score": score,
        "passed_count": passed_count,
        "total_rules": len(DOCTRINE_RULES),
        "checks": checks,
        "violations": violations,
        "critical_violation_count": len(critical_violations),
        "required_next_step": _required_next_step(violations, critical_violations),
    }


def build_doctrine_check(payload: dict[str, Any]) -> dict[str, Any]:
    plan = payload.get("plan")

    if not plan:
        from backend.core.response_planner import build_response_plan

        plan = build_response_plan(payload)

    if not isinstance(plan, dict):
        raise ValueError("plan must be an object")

    return {
        "status": "ok",
        "module": "doctrine_check",
        "version": DOCTRINE_ENFORCER_VERSION,
        "plan": plan,
        "doctrine": check_doctrine(plan),
    }


def _required_fix(rule_id: str) -> str:
    fixes = {
        "human_accountability": "Add explicit human accountability language.",
        "uncertainty_disclosure": "Add confidence, uncertainty, or limitation language.",
        "evidence_standard": "Separate facts, assumptions, risks, and recommendations.",
        "approval_gate": "Add approval requirement before irreversible execution.",
        "capability_growth": "Add capability-building or teaching element.",
    }
    return fixes.get(rule_id, "Review doctrine rule and revise plan.")


def _required_next_step(
    violations: list[dict[str, Any]],
    critical_violations: list[dict[str, Any]],
) -> str:
    if critical_violations:
        return "Revise plan before proceeding. Critical doctrine violation present."
    if violations:
        return "Revise plan or proceed with caution after noting doctrine gaps."
    return "Doctrine check passed. Proceed according to execution gate."
