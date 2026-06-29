from dataclasses import dataclass


@dataclass
class MedicalIntelligenceAgent:
    name: str = "Medical Intelligence Agent"
    mission: str = "Support the Medical Intelligence Directorate."
    status: str = "active"


AGENT = MedicalIntelligenceAgent()
