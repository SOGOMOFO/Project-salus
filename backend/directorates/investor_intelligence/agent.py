from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class PanelAnalyst:
    name: str
    metric: str
    lens: str

    def evaluate(self, scores: dict[str, int]) -> dict[str, str]:
        score = scores.get(self.metric, 50)
        sentiment = "constructive" if score >= 70 else "cautious" if score >= 50 else "defensive"
        return {
            "analyst": self.name,
            "focus": self.lens,
            "view": f"{self.name} is {sentiment} with {self.metric} score at {score}.",
        }


class ValueAnalyst(PanelAnalyst):
    def __init__(self) -> None:
        super().__init__("Value Analyst", "valuation", "Intrinsic value and margin of safety")


class GrowthAnalyst(PanelAnalyst):
    def __init__(self) -> None:
        super().__init__("Growth Analyst", "growth", "Revenue, earnings, and TAM expansion")


class MacroStrategist(PanelAnalyst):
    def __init__(self) -> None:
        super().__init__("Macro Strategist", "macro_environment", "Rates, liquidity, and policy context")


class BehavioralEconomist(PanelAnalyst):
    def __init__(self) -> None:
        super().__init__("Behavioral Economist", "conviction", "Narrative risk and sentiment discipline")


class RiskOfficer(PanelAnalyst):
    def __init__(self) -> None:
        super().__init__("Risk Officer", "risk", "Downside protection and volatility control")


class PortfolioManager(PanelAnalyst):
    def __init__(self) -> None:
        super().__init__("Portfolio Manager", "financial_strength", "Sizing and portfolio construction fit")


def build_expert_panel() -> list[PanelAnalyst]:
    return [
        ValueAnalyst(),
        GrowthAnalyst(),
        MacroStrategist(),
        BehavioralEconomist(),
        RiskOfficer(),
        PortfolioManager(),
    ]


def panel_names() -> list[str]:
    return [analyst.name for analyst in build_expert_panel()]
