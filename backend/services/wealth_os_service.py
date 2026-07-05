from typing import Any, Dict, List


DOLLAR_MISSIONS = [
    "security_cash",
    "operating_cash",
    "debt_attack",
    "index_investing",
    "human_capital",
    "business_capital",
    "speculative_capital",
    "dead_money",
]

HIGH_INTEREST_DEBT_APR = 8.0


def safe_float(value: Any) -> float:
    try:
        return max(0.0, float(value))
    except (TypeError, ValueError):
        return 0.0


def round_money(value: float) -> float:
    return round(value, 2)


def classify_single_dollar(payload: Dict[str, Any]) -> Dict[str, Any]:
    amount = safe_float(payload.get("amount"))
    emergency_months = safe_float(payload.get("emergency_months"))
    target_emergency_months = safe_float(payload.get("target_emergency_months", 6))
    highest_debt_apr = safe_float(payload.get("highest_debt_apr"))
    timeframe = str(payload.get("timeframe", "long_term")).lower()
    goal = str(payload.get("goal", "wealth_building")).lower()
    risk_tolerance = str(payload.get("risk_tolerance", "medium")).lower()

    if amount <= 0:
        mission = "dead_money"
        rationale = "No deployable amount provided."
    elif emergency_months < target_emergency_months:
        mission = "security_cash"
        rationale = "Emergency reserves are below target."
    elif highest_debt_apr >= HIGH_INTEREST_DEBT_APR:
        mission = "debt_attack"
        rationale = "High-interest debt creates a strong guaranteed-return target."
    elif timeframe in {"immediate", "short_term", "0_12_months"}:
        mission = "operating_cash"
        rationale = "Money needed within 12 months should not be exposed to market risk."
    elif goal == "human_capital":
        mission = "human_capital"
        rationale = "Skill, credential, and earning-power investments can create high ROI."
    elif goal == "business_growth":
        mission = "business_capital"
        rationale = "Capital supports Echo Seven or Project Salus growth."
    elif goal == "speculative" and risk_tolerance == "high":
        mission = "speculative_capital"
        rationale = "Speculative capital is allowed only after core protection is covered."
    elif goal in {"wealth_building", "retirement", "legacy"}:
        mission = "index_investing"
        rationale = "Long-term surplus should compound in diversified assets."
    else:
        mission = "dead_money"
        rationale = "No clear strategic mission assigned."

    return {
        "amount": round_money(amount),
        "assigned_mission": mission,
        "rationale": rationale,
        "approved_missions": DOLLAR_MISSIONS,
        "doctrine": "Every dollar must have a mission.",
    }


def build_cash_allocation(payload: Dict[str, Any]) -> Dict[str, Any]:
    cash_available = safe_float(payload.get("cash_available"))
    monthly_expenses = safe_float(payload.get("monthly_expenses"))
    current_emergency_cash = safe_float(payload.get("current_emergency_cash"))
    target_emergency_months = safe_float(payload.get("target_emergency_months", 6))
    upcoming_obligations_90_days = safe_float(payload.get("upcoming_obligations_90_days"))
    high_interest_debt_balance = safe_float(payload.get("high_interest_debt_balance"))
    human_capital_need = safe_float(payload.get("human_capital_need"))
    business_capital_need = safe_float(payload.get("business_capital_need"))
    speculative_cap_percent = min(safe_float(payload.get("speculative_cap_percent", 10)), 20)

    remaining = cash_available
    allocations: Dict[str, float] = {mission: 0.0 for mission in DOLLAR_MISSIONS}

    target_emergency_cash = monthly_expenses * target_emergency_months
    emergency_gap = max(0.0, target_emergency_cash - current_emergency_cash)

    security_allocation = min(remaining, emergency_gap)
    allocations["security_cash"] = security_allocation
    remaining -= security_allocation

    operating_allocation = min(remaining, upcoming_obligations_90_days)
    allocations["operating_cash"] = operating_allocation
    remaining -= operating_allocation

    debt_allocation = min(remaining, high_interest_debt_balance)
    allocations["debt_attack"] = debt_allocation
    remaining -= debt_allocation

    human_capital_allocation = min(remaining, human_capital_need)
    allocations["human_capital"] = human_capital_allocation
    remaining -= human_capital_allocation

    business_capital_allocation = min(remaining, business_capital_need)
    allocations["business_capital"] = business_capital_allocation
    remaining -= business_capital_allocation

    speculative_cap = remaining * (speculative_cap_percent / 100)
    allocations["speculative_capital"] = speculative_cap
    remaining -= speculative_cap

    allocations["index_investing"] = remaining
    allocations["dead_money"] = 0.0

    risk_flags: List[str] = []

    if emergency_gap > 0:
        risk_flags.append("Emergency fund below target.")

    if high_interest_debt_balance > 0:
        risk_flags.append("High-interest debt should be reviewed before excess investing.")

    if cash_available > 0 and monthly_expenses == 0:
        risk_flags.append("Monthly expenses missing; cash-readiness calculation may be incomplete.")

    if speculative_cap_percent > 10:
        risk_flags.append("Speculative allocation above default guardrail.")

    rounded_allocations = {k: round_money(v) for k, v in allocations.items()}

    return {
        "cash_available": round_money(cash_available),
        "monthly_expenses": round_money(monthly_expenses),
        "target_emergency_cash": round_money(target_emergency_cash),
        "current_emergency_cash": round_money(current_emergency_cash),
        "emergency_gap": round_money(emergency_gap),
        "allocations": rounded_allocations,
        "risk_flags": risk_flags,
        "doctrine": "Security first, compounding second, speculation last.",
        "next_action": build_next_action(rounded_allocations, risk_flags),
    }


def build_next_action(allocations: Dict[str, float], risk_flags: List[str]) -> str:
    if allocations.get("security_cash", 0) > 0:
        return "Fund emergency reserves first."

    if allocations.get("debt_attack", 0) > 0:
        return "Attack high-interest debt before expanding speculative exposure."

    if allocations.get("human_capital", 0) > 0:
        return "Deploy approved funds toward skills, certifications, or earning-power upgrades."

    if allocations.get("business_capital", 0) > 0:
        return "Deploy approved funds toward Echo Seven or Project Salus growth."

    if allocations.get("index_investing", 0) > 0:
        return "Move long-term surplus toward diversified compounding assets."

    if risk_flags:
        return "Resolve risk flags before assigning additional capital."

    return "No action required."
