from __future__ import annotations

from typing import Any


def classify_intent(text: str) -> dict[str, Any]:
    value = text.strip().lower()

    if any(word in value for word in ["learn", "study", "school", "wgu", "psp", "teach"]):
        intent = "learning"
        layer = "learning"
    elif any(word in value for word in ["decide", "should i", "risk", "recommend", "option", "decision"]):
        intent = "judgment"
        layer = "reasoning"
    elif any(word in value for word in ["remember", "memory", "context"]):
        intent = "memory"
        layer = "memory"
    elif any(word in value for word in ["mission", "today", "priority", "execute"]):
        intent = "command"
        layer = "command"
    elif any(word in value for word in ["agent", "commander", "cyber", "finance", "teacher"]):
        intent = "agent"
        layer = "execution"
    else:
        intent = "general"
        layer = "command"

    return {
        "intent": intent,
        "layer": layer,
        "confidence": "medium",
        "input_length": len(text),
    }
