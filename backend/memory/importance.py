from __future__ import annotations

from typing import Optional


def calculate_importance(*, content: str, tags: Optional[list[str]] = None, source: Optional[str] = None) -> float:
    text = str(content or "")
    normalized_tags = [str(tag).strip().lower() for tag in (tags or []) if str(tag).strip()]
    score = 0.3

    length_bonus = min(0.2, len(text) / 1500.0)
    score += length_bonus

    if normalized_tags:
        score += min(0.2, 0.05 * len(normalized_tags))

    high_priority_tags = {"important", "urgent", "critical", "mission", "investor-intelligence"}
    if any(tag in high_priority_tags for tag in normalized_tags):
        score += 0.2

    if source:
        score += 0.05

    return round(max(0.0, min(1.0, score)), 3)
