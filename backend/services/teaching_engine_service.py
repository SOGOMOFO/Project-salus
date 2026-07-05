from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import json


TEACHING_ENGINE_VERSION = "1.0.0"
TEACHING_SESSION_STORE = Path("runtime/teaching_engine_sessions.json")

VALID_LEVELS = {"beginner", "intermediate", "advanced"}
VALID_MODES = {
    "explain",
    "guided_practice",
    "quiz",
    "review",
    "mission_training",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ensure_store() -> None:
    TEACHING_SESSION_STORE.parent.mkdir(parents=True, exist_ok=True)
    if not TEACHING_SESSION_STORE.exists():
        TEACHING_SESSION_STORE.write_text("[]")


def _load_sessions() -> list[dict[str, Any]]:
    _ensure_store()

    try:
        data = json.loads(TEACHING_SESSION_STORE.read_text())
    except json.JSONDecodeError:
        return []

    if not isinstance(data, list):
        return []

    return [item for item in data if isinstance(item, dict)]


def _save_sessions(sessions: list[dict[str, Any]]) -> None:
    _ensure_store()
    TEACHING_SESSION_STORE.write_text(json.dumps(sessions, indent=2, sort_keys=True))


def teaching_engine_status() -> dict[str, Any]:
    sessions = _load_sessions()

    return {
        "status": "ok",
        "module": "teaching_engine",
        "version": TEACHING_ENGINE_VERSION,
        "mission": "Teach Kyle in a way that increases capability and reduces dependence on AI.",
        "supported_modes": sorted(VALID_MODES),
        "supported_levels": sorted(VALID_LEVELS),
        "session_count": len(sessions),
        "store": str(TEACHING_SESSION_STORE),
    }


def build_learning_profile(payload: dict[str, Any]) -> dict[str, Any]:
    topic = str(payload.get("topic", "general capability")).strip() or "general capability"
    level = str(payload.get("level", "beginner")).strip().lower()
    goal = str(payload.get("goal", "understand and apply the topic")).strip()
    constraints = payload.get("constraints", [])

    if level not in VALID_LEVELS:
        level = "beginner"

    if isinstance(constraints, str):
        constraints = [item.strip() for item in constraints.split(",") if item.strip()]
    elif isinstance(constraints, list):
        constraints = [str(item).strip() for item in constraints if str(item).strip()]
    else:
        constraints = []

    return {
        "status": "ok",
        "module": "teaching_engine",
        "profile": {
            "learner": str(payload.get("user", "Kyle")).strip() or "Kyle",
            "topic": topic,
            "level": level,
            "goal": goal,
            "constraints": constraints,
            "teaching_style": [
                "plain language",
                "small steps",
                "examples first",
                "practice questions",
                "brief correction",
                "mission relevance",
            ],
            "success_standard": "Kyle can explain it, apply it, and make a better decision without over-relying on AI.",
        },
    }


def build_lesson(payload: dict[str, Any]) -> dict[str, Any]:
    profile = build_learning_profile(payload)["profile"]
    topic = profile["topic"]
    level = profile["level"]

    return {
        "status": "ok",
        "module": "teaching_engine",
        "lesson": {
            "title": f"{topic.title()} — {level.title()} Lesson",
            "objective": f"Understand the core idea of {topic} and apply it in a realistic Project Salus / life mission context.",
            "explanation": _explanation_for_topic(topic, level),
            "example": _example_for_topic(topic),
            "practice": [
                f"Explain {topic} in your own words.",
                f"Identify one real situation where {topic} matters.",
                f"Choose the safest next action using {topic}.",
            ],
            "commander_takeaway": f"Do not just memorize {topic}. Use it to improve judgment, decisions, and execution.",
            "next_step": "Answer the practice question or request a quiz.",
        },
    }


def build_quiz(payload: dict[str, Any]) -> dict[str, Any]:
    profile = build_learning_profile(payload)["profile"]
    topic = profile["topic"]

    return {
        "status": "ok",
        "module": "teaching_engine",
        "quiz": {
            "topic": topic,
            "instructions": "Answer one question at a time. The system should correct briefly and continue.",
            "questions": [
                {
                    "id": "q1",
                    "type": "short_answer",
                    "question": f"What is the main purpose of {topic}?",
                    "answer_key": "The answer should explain the practical purpose and not just define the term.",
                },
                {
                    "id": "q2",
                    "type": "scenario",
                    "question": f"Give one real-world example where {topic} affects a decision.",
                    "answer_key": "The answer should connect the concept to a decision, risk, or outcome.",
                },
                {
                    "id": "q3",
                    "type": "application",
                    "question": f"What is the next action you would take using {topic}?",
                    "answer_key": "The answer should include a clear, safe, useful next action.",
                },
            ],
        },
    }


def create_teaching_session(payload: dict[str, Any]) -> dict[str, Any]:
    mode = str(payload.get("mode", "explain")).strip().lower()
    if mode not in VALID_MODES:
        mode = "explain"

    profile = build_learning_profile(payload)["profile"]
    lesson = build_lesson(payload)["lesson"]
    quiz = build_quiz(payload)["quiz"] if mode in {"quiz", "guided_practice", "mission_training"} else None

    session = {
        "id": str(payload.get("id") or uuid4()),
        "module": "teaching_engine",
        "version": TEACHING_ENGINE_VERSION,
        "mode": mode,
        "profile": profile,
        "lesson": lesson,
        "quiz": quiz,
        "created_at": _now_iso(),
        "kernel_alignment": {
            "prime_directive": "Improve human judgment without replacing human accountability.",
            "capability_growth": True,
            "non_execution_rule": "Teaching sessions produce learning plans, not irreversible external actions.",
        },
    }

    sessions = _load_sessions()

    if session["id"] in {existing.get("id") for existing in sessions}:
        raise ValueError("teaching session id already exists")

    sessions.append(session)
    _save_sessions(sessions)

    return session


def list_teaching_sessions(topic: str | None = None, mode: str | None = None) -> list[dict[str, Any]]:
    sessions = _load_sessions()

    if topic:
        value = topic.strip().lower()
        sessions = [
            session for session in sessions
            if value in str(session.get("profile", {}).get("topic", "")).lower()
        ]

    if mode:
        value = mode.strip().lower()
        sessions = [
            session for session in sessions
            if str(session.get("mode", "")).lower() == value
        ]

    return sorted(sessions, key=lambda item: str(item.get("created_at", "")), reverse=True)


def get_teaching_session(session_id: str) -> dict[str, Any] | None:
    for session in _load_sessions():
        if session.get("id") == session_id:
            return session
    return None


def _explanation_for_topic(topic: str, level: str) -> str:
    return (
        f"{topic} should be learned as a usable mental tool. "
        f"At the {level} level, focus on the definition, why it matters, "
        "how it changes decisions, and what mistakes to avoid."
    )


def _example_for_topic(topic: str) -> str:
    return (
        f"Example: If the topic is {topic}, Salus should help Kyle connect it to a real mission, "
        "identify the risk, choose a next action, and review the outcome afterward."
    )
