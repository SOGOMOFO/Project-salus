SCENARIO_PLACEHOLDERS = {
    "recession": "placeholder",
    "inflation_shock": "placeholder",
    "market_crash": "placeholder",
    "interest_rate_change": "placeholder",
    "geopolitical_conflict": "placeholder",
    "ai_adoption_acceleration": "placeholder",
}


def run_scenarios(scores: dict[str, int]) -> dict[str, str]:
    risk = scores.get("risk", 50)
    growth = scores.get("growth", 50)
    macro = scores.get("macro_environment", 50)

    recession = "stressed" if macro < 50 or risk > 65 else "resilient"
    inflation = "sensitive" if macro < 45 else "moderate"
    crash = "defensive-needed" if risk > 70 else "watchlist"
    rates = "vulnerable" if growth > 75 and macro < 55 else "balanced"
    geo = "elevated-risk" if risk > 60 else "contained"
    ai_adoption = "tailwind" if growth > 70 else "uncertain"

    return {
        "recession": recession,
        "inflation_shock": inflation,
        "market_crash": crash,
        "interest_rate_change": rates,
        "geopolitical_conflict": geo,
        "ai_adoption_acceleration": ai_adoption,
    }
