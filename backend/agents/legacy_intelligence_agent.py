from dataclasses import dataclass


@dataclass
class LegacyIntelligenceAgent:
    name: str = "Legacy Intelligence Agent"
    mission: str = "Support the Legacy Intelligence Directorate."
    status: str = "active"


AGENT = LegacyIntelligenceAgent()
