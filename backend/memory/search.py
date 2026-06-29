from __future__ import annotations

import re
from typing import Any


def _tokenize(text: str) -> set[str]:
	return {token for token in re.split(r"[^a-zA-Z0-9]+", text.lower()) if token}


def semantic_search_memories(
	query: str,
	memories: list[dict[str, Any]],
	*,
	limit: int = 10,
) -> list[dict[str, Any]]:
	query_tokens = _tokenize(str(query or ""))
	if not query_tokens:
		return []

	scored: list[tuple[float, dict[str, Any]]] = []
	for memory in memories:
		title_tokens = _tokenize(str(memory.get("title", "")))
		content_tokens = _tokenize(str(memory.get("content", "")))
		tags_tokens = _tokenize(" ".join(memory.get("tags", [])))
		all_tokens = title_tokens | content_tokens | tags_tokens
		if not all_tokens:
			continue

		overlap = len(query_tokens & all_tokens)
		if overlap == 0:
			continue

		score = overlap / max(1, len(query_tokens | all_tokens))
		enriched = dict(memory)
		enriched["semantic_score"] = round(score, 4)
		scored.append((score, enriched))

	scored.sort(key=lambda row: row[0], reverse=True)
	return [row[1] for row in scored[: max(1, int(limit))]]
