from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Literal
import json
import uuid


BASE_DIR = Path(__file__).resolve().parent
EVENT_LOG = BASE_DIR / "improvement_events.jsonl"
PROPOSAL_LOG = BASE_DIR / "improvement_proposals.jsonl"


Severity = Literal["low", "medium", "high", "critical"]
IssueType = Literal[
    "accuracy",
    "workflow",
    "prompt",
    "knowledge_base",
    "code",
    "security",
    "user_experience",
    "decision_quality",
    "other",
]


PROTECTED_CHANGE_TERMS = [
    "core doctrine",
    "financial decision",
    "legal strategy",
    "medical guidance",
    "security permission",
    "production code",
    "external action",
    "send email",
    "payment",
    "contract",
    "account access",
]


@dataclass
class ImprovementEvent:
    id: str
    created_at: str
    source: str
    issue_type: IssueType
    description: str
    severity: Severity
    affected_agent: Optional[str] = None
    evidence: Optional[str] = None
    status: str = "logged"


@dataclass
class ImprovementProposal:
    id: str
    event_id: str
    created_at: str
    proposed_change: str
    strategic_fit_score: int
    roi_score: int
    risk_score: int
    difficulty_score: int
    recommendation: str
    requires_kyle_approval: bool
    approved_by_kyle: bool = False
    status: str = "pending_review"


class SalusImprovementEngine:
    """
    Controlled recursive self-improvement engine.

    This does NOT let Project Salus rewrite itself autonomously.
    It creates a gated improvement loop:
    observe -> evaluate -> propose -> score -> approve -> implement later.
    """

    def log_event(
        self,
        source: str,
        issue_type: IssueType,
        description: str,
        severity: Severity = "medium",
        affected_agent: Optional[str] = None,
        evidence: Optional[str] = None,
    ) -> ImprovementEvent:
        event = ImprovementEvent(
            id=str(uuid.uuid4()),
            created_at=self._now(),
            source=source,
            issue_type=issue_type,
            description=description,
            severity=severity,
            affected_agent=affected_agent,
            evidence=evidence,
        )
        self._append_jsonl(EVENT_LOG, asdict(event))
        return event

    def generate_proposal(
        self,
        event: ImprovementEvent,
        proposed_change: Optional[str] = None,
    ) -> ImprovementProposal:
        change = proposed_change or self._default_proposal(event)

        strategic_fit = self._score_strategic_fit(event, change)
        roi = self._score_roi(event, change)
        risk = self._score_risk(event, change)
        difficulty = self._score_difficulty(event, change)

        requires_approval = self._requires_kyle_approval(event, change, risk)
        recommendation = self._recommend(strategic_fit, roi, risk, difficulty)

        proposal = ImprovementProposal(
            id=str(uuid.uuid4()),
            event_id=event.id,
            created_at=self._now(),
            proposed_change=change,
            strategic_fit_score=strategic_fit,
            roi_score=roi,
            risk_score=risk,
            difficulty_score=difficulty,
            recommendation=recommendation,
            requires_kyle_approval=requires_approval,
        )

        self._append_jsonl(PROPOSAL_LOG, asdict(proposal))
        return proposal

    def list_events(self) -> list[dict]:
        return self._read_jsonl(EVENT_LOG)

    def list_proposals(self) -> list[dict]:
        return self._read_jsonl(PROPOSAL_LOG)

    def _default_proposal(self, event: ImprovementEvent) -> str:
        if event.issue_type == "accuracy":
            return "Add a verification checkpoint before answering similar requests."
        if event.issue_type == "workflow":
            return "Convert the repeated workflow into a reusable SOP."
        if event.issue_type == "prompt":
            return "Revise the agent prompt to reduce ambiguity and improve output consistency."
        if event.issue_type == "knowledge_base":
            return "Add the confirmed lesson to the Project Salus knowledge base."
        if event.issue_type == "code":
            return "Create a tested patch proposal before changing live code."
        if event.issue_type == "security":
            return "Add a security review gate before implementation."
        if event.issue_type == "decision_quality":
            return "Add a structured decision scorecard with risk, ROI, difficulty, and opportunity cost."
        if event.issue_type == "user_experience":
            return "Simplify the user flow and reduce unnecessary steps."
        return "Create an improvement proposal and route it through review."

    def _score_strategic_fit(self, event: ImprovementEvent, change: str) -> int:
        score = 3
        if event.issue_type in ["accuracy", "decision_quality", "security"]:
            score += 2
        if "Project Salus" in change or "Salus" in change:
            score += 1
        return min(score, 5)

    def _score_roi(self, event: ImprovementEvent, change: str) -> int:
        score = 3
        if event.severity in ["high", "critical"]:
            score += 1
        if event.issue_type in ["workflow", "prompt", "accuracy", "decision_quality"]:
            score += 1
        return min(score, 5)

    def _score_risk(self, event: ImprovementEvent, change: str) -> int:
        score = 2
        text = f"{event.description} {change}".lower()

        if event.issue_type in ["security", "code"]:
            score += 1
        if event.severity == "critical":
            score += 2
        elif event.severity == "high":
            score += 1

        for term in PROTECTED_CHANGE_TERMS:
            if term in text:
                score += 2

        return min(score, 5)

    def _score_difficulty(self, event: ImprovementEvent, change: str) -> int:
        if event.issue_type in ["prompt", "workflow", "knowledge_base"]:
            return 2
        if event.issue_type in ["code", "security"]:
            return 4
        return 3

    def _requires_kyle_approval(
        self,
        event: ImprovementEvent,
        change: str,
        risk_score: int,
    ) -> bool:
        text = f"{event.description} {change}".lower()

        if risk_score >= 4:
            return True
        if event.severity in ["high", "critical"]:
            return True
        if event.issue_type in ["code", "security"]:
            return True
        return any(term in text for term in PROTECTED_CHANGE_TERMS)

    def _recommend(
        self,
        strategic_fit: int,
        roi: int,
        risk: int,
        difficulty: int,
    ) -> str:
        if risk >= 5:
            return "Pause"
        if strategic_fit >= 4 and roi >= 4 and risk <= 3:
            return "Pursue"
        if strategic_fit >= 3 and roi >= 3 and difficulty >= 4:
            return "Delegate"
        if strategic_fit <= 2 or roi <= 2:
            return "Discard"
        return "Pause"

    def _append_jsonl(self, path: Path, data: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

    def _read_jsonl(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    engine = SalusImprovementEngine()

    event = engine.log_event(
        source="manual_test",
        issue_type="decision_quality",
        description="Project Salus needs a repeatable way to improve after errors and friction.",
        severity="medium",
        affected_agent="mission_control",
        evidence="User requested recursive self-improvement.",
    )

    proposal = engine.generate_proposal(event)

    print("Improvement event created:")
    print(json.dumps(asdict(event), indent=2))

    print("\nImprovement proposal created:")
    print(json.dumps(asdict(proposal), indent=2))
