from __future__ import annotations


def compute_risk_reward(scores: dict[str, int]) -> dict[str, float | bool]:
    upside = (scores["growth"] + scores["competitive_moat"] + scores["conviction"]) / 3.0
    downside = float(scores["risk"])
    spread = round(upside - downside, 2)
    exceptional = bool(spread >= 18 and scores["conviction"] >= 75)
    return {
        "upside_proxy": round(upside, 2),
        "downside_proxy": round(downside, 2),
        "spread": spread,
        "exceptional": exceptional,
    }


def synthesize_risks(scores: dict[str, int], submitted_risks: list[str]) -> list[str]:
    risks = [risk for risk in submitted_risks if str(risk).strip()]
    if scores["risk"] >= 70:
        risks.append("Elevated drawdown risk based on current volatility and uncertainty profile.")
    if scores["macro_environment"] < 45:
        risks.append("Macro backdrop appears fragile and may pressure multiples.")
    if scores["technical_trend"] < 40:
        risks.append("Technical trend is weak and may indicate timing risk.")
    if not risks:
        risks.append("No dominant risk flagged; continue monitoring execution and macro changes.")
    return risks[:5]
