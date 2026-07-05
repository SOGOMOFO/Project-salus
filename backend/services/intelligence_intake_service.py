from typing import Any, Dict, List


SOURCE_TYPES = [
    "video",
    "podcast",
    "article",
    "book",
    "social_post",
    "research_paper",
    "conversation",
    "internal_note",
    "file",
    "other",
]

EVIDENCE_LEVELS = [
    "verified_fact",
    "strong_evidence",
    "expert_opinion",
    "emerging_theory",
    "ai_generated_pattern",
    "speculation",
    "unverified_claim",
]

TRIAGE_RECOMMENDATIONS = [
    "USE_NOW",
    "VERIFY_FIRST",
    "PARK",
    "DISCARD",
    "CONVERT_TO_MISSION",
    "CONVERT_TO_DOCTRINE_CANDIDATE",
]

ROUTES = [
    "decision_firewall",
    "strategy_critical_thinking",
    "ai_governance",
    "wealth_os",
    "echo_seven_assessment",
    "mission_execution",
    "mission_registry",
    "doctrine_registry",
    "curiosity_parking_lot",
]

HYPE_TERMS = [
    "shocked",
    "terrified",
    "secret",
    "hidden",
    "guaranteed",
    "nobody talks about",
    "last chance",
    "before it's too late",
    "easy money",
    "effortless",
    "one trick",
    "decoded",
    "they don't want you to know",
]

HIGH_RISK_TOPICS = [
    "money",
    "investing",
    "crypto",
    "medical",
    "health",
    "legal",
    "tax",
    "ai safety",
    "superintelligence",
    "cybersecurity",
    "password",
    "credentials",
    "religion",
    "politics",
    "business",
]


def normalize_list(values: Any) -> List[str]:
    if not values:
        return []

    if isinstance(values, list):
        return [str(v).strip() for v in values if str(v).strip()]

    return [str(values).strip()]


def normalize_choice(value: Any, allowed: List[str], default: str) -> str:
    normalized = str(value or default).strip().lower()

    if normalized not in allowed:
        return default

    return normalized


def clamp_score(value: Any) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError):
        return 0

    return max(0, min(score, 10))


def estimate_evidence_level(payload: Dict[str, Any]) -> str:
    provided = str(payload.get("evidence_level", "")).strip().lower()

    if provided in EVIDENCE_LEVELS:
        return provided

    citations = normalize_list(payload.get("citations"))
    source_type = normalize_choice(payload.get("source_type"), SOURCE_TYPES, "other")
    author_credentials = str(payload.get("author_credentials", "")).strip()

    if source_type == "research_paper" and citations:
        return "strong_evidence"

    if citations and author_credentials:
        return "expert_opinion"

    if citations:
        return "emerging_theory"

    return "unverified_claim"


def detect_hype_flags(text: str) -> List[str]:
    lowered = text.lower()
    flags: List[str] = []

    for term in HYPE_TERMS:
        if term in lowered:
            flags.append(f"hype_term_detected:{term}")

    return flags


def detect_topic_risks(text: str, topics: List[str]) -> List[str]:
    lowered = text.lower()
    combined_topics = [topic.lower() for topic in topics]
    risks: List[str] = []

    for topic in HIGH_RISK_TOPICS:
        if topic in lowered or topic in combined_topics:
            risks.append(f"high_impact_topic:{topic}")

    return sorted(set(risks))


def extract_claim_candidates(payload: Dict[str, Any]) -> List[str]:
    explicit_claims = normalize_list(payload.get("claims"))

    if explicit_claims:
        return explicit_claims

    summary = str(payload.get("summary", "")).strip()
    title = str(payload.get("title", "")).strip()

    claims: List[str] = []

    if title:
        claims.append(title)

    if summary:
        sentences = [
            item.strip()
            for item in summary.replace("?", ".").replace("!", ".").split(".")
            if item.strip()
        ]

        claims.extend(sentences[:5])

    return claims[:10]


def build_verification_plan(
    evidence_level: str,
    claims: List[str],
    source_type: str,
    risk_flags: List[str],
) -> List[str]:
    plan: List[str] = []

    if evidence_level in {"unverified_claim", "speculation", "ai_generated_pattern", "emerging_theory"}:
        plan.append("Find primary sources or original data before operational use.")

    if source_type in {"video", "podcast", "social_post"}:
        plan.append("Separate transcript claims from creator framing and marketing language.")

    if claims:
        plan.append("Verify the top claim: " + claims[0])

    if any(flag.startswith("hype_term_detected") for flag in risk_flags):
        plan.append("Remove emotional framing and restate the claim in neutral language.")

    if any(flag.startswith("high_impact_topic") for flag in risk_flags):
        plan.append("Route high-impact claims through Decision Firewall or Strategy Directorate.")

    if not plan:
        plan.append("Document source and monitor for confirmation or contradiction.")

    return plan


def calculate_signal_score(payload: Dict[str, Any], evidence_level: str, risk_flags: List[str]) -> int:
    strategic_fit = clamp_score(payload.get("strategic_fit"))
    actionability = clamp_score(payload.get("actionability"))
    novelty = clamp_score(payload.get("novelty"))
    relevance = clamp_score(payload.get("relevance"))
    source_trust = clamp_score(payload.get("source_trust"))

    evidence_weights = {
        "verified_fact": 10,
        "strong_evidence": 9,
        "expert_opinion": 7,
        "emerging_theory": 5,
        "ai_generated_pattern": 3,
        "speculation": 2,
        "unverified_claim": 1,
    }

    risk_penalty = min(30, len(risk_flags) * 5)

    weighted = (
        strategic_fit * 0.25
        + actionability * 0.20
        + relevance * 0.20
        + source_trust * 0.15
        + novelty * 0.08
        + evidence_weights[evidence_level] * 0.12
    )

    score = round(weighted * 10) - risk_penalty
    return max(0, min(score, 100))


def recommend_route(payload: Dict[str, Any], signal_score: int, evidence_level: str, risk_flags: List[str]) -> Dict[str, Any]:
    strategic_fit = clamp_score(payload.get("strategic_fit"))
    actionability = clamp_score(payload.get("actionability"))
    source_type = normalize_choice(payload.get("source_type"), SOURCE_TYPES, "other")
    topics = [topic.lower() for topic in normalize_list(payload.get("topics"))]

    high_impact = any(flag.startswith("high_impact_topic") for flag in risk_flags)
    weak_evidence = evidence_level in {"unverified_claim", "speculation", "ai_generated_pattern"}
    hype_present = any(flag.startswith("hype_term_detected") for flag in risk_flags)

    # Highest-priority rule:
    # Weak evidence + hype + high-impact topic should be verified, not discarded.
    # This preserves potentially important material while blocking premature action.
    if weak_evidence and hype_present and high_impact:
        return {
            "recommended_route": "decision_firewall",
            "recommendation": "VERIFY_FIRST",
        }

    if source_type == "research_paper" and signal_score >= 70:
        return {
            "recommended_route": "strategy_critical_thinking",
            "recommendation": "VERIFY_FIRST",
        }

    if "doctrine" in topics or "lesson" in topics:
        return {
            "recommended_route": "doctrine_registry",
            "recommendation": "CONVERT_TO_DOCTRINE_CANDIDATE",
        }

    if signal_score >= 65 and actionability >= 7 and not weak_evidence:
        return {
            "recommended_route": "mission_execution",
            "recommendation": "CONVERT_TO_MISSION",
        }

    if "ai" in topics or "ai governance" in topics or "ai safety" in topics:
        if high_impact:
            return {
                "recommended_route": "ai_governance",
                "recommendation": "VERIFY_FIRST",
            }

    if "wealth" in topics or "investing" in topics or "money" in topics:
        if high_impact:
            return {
                "recommended_route": "wealth_os",
                "recommendation": "VERIFY_FIRST",
            }

    if "echo seven" in topics or "business" in topics:
        if signal_score >= 55:
            return {
                "recommended_route": "echo_seven_assessment",
                "recommendation": "VERIFY_FIRST",
            }

    if signal_score < 35 and strategic_fit < 5:
        return {
            "recommended_route": "curiosity_parking_lot",
            "recommendation": "DISCARD",
        }

    if weak_evidence and strategic_fit < 5:
        return {
            "recommended_route": "curiosity_parking_lot",
            "recommendation": "PARK",
        }

    return {
        "recommended_route": "curiosity_parking_lot",
        "recommendation": "PARK",
    }


def build_mission_candidate(payload: Dict[str, Any], claims: List[str], route: Dict[str, Any]) -> Dict[str, Any]:
    title = payload.get("title", "Untitled Intelligence Item")

    if route["recommendation"] != "CONVERT_TO_MISSION":
        return {}

    return {
        "title": f"Validate intelligence item: {title}",
        "objective": "Convert high-signal intelligence into a controlled execution test.",
        "source": "intelligence_intake",
        "owner": payload.get("owner", "Kyle"),
        "status": "planned",
        "strategic_fit": clamp_score(payload.get("strategic_fit")),
        "roi": clamp_score(payload.get("roi")),
        "urgency": clamp_score(payload.get("urgency")),
        "risk": clamp_score(payload.get("risk")),
        "difficulty": clamp_score(payload.get("difficulty")),
        "opportunity_cost": clamp_score(payload.get("opportunity_cost")),
        "success_criteria": [
            "Top claim verified or rejected.",
            "One practical next action identified.",
        ],
        "next_actions": [
            "Verify the top claim: " + claims[0] if claims else "Verify the central claim."
        ],
    }


def build_doctrine_candidate(payload: Dict[str, Any], claims: List[str], route: Dict[str, Any]) -> Dict[str, Any]:
    topics = [topic.lower() for topic in normalize_list(payload.get("topics"))]

    if route["recommendation"] != "CONVERT_TO_DOCTRINE_CANDIDATE" and "doctrine" not in topics:
        return {}

    statement = claims[0] if claims else payload.get("summary", "")

    return {
        "title": f"Doctrine candidate: {payload.get('title', 'Untitled Intelligence Item')}",
        "statement": statement,
        "category": infer_doctrine_category(topics),
        "status": "proposed",
        "evidence_level": estimate_evidence_level(payload),
        "source": "intelligence_intake",
        "rationale": payload.get("summary", ""),
        "triggers": ["intelligence_intake"],
        "rules": [statement] if statement else [],
        "risks_if_ignored": ["Useful lesson may not be retained."],
        "confidence_score": min(7, clamp_score(payload.get("source_trust"))),
    }


def infer_doctrine_category(topics: List[str]) -> str:
    if "ai" in topics or "ai governance" in topics or "ai safety" in topics:
        return "ai_governance"

    if "wealth" in topics or "investing" in topics or "money" in topics:
        return "wealth"

    if "family" in topics:
        return "family"

    if "mission" in topics or "execution" in topics:
        return "mission_execution"

    if "echo seven" in topics or "business" in topics:
        return "echo_seven"

    if "strategy" in topics or "critical thinking" in topics:
        return "strategy"

    return "general"


def triage_intelligence(payload: Dict[str, Any]) -> Dict[str, Any]:
    title = payload.get("title", "Untitled Intelligence Item")
    summary = payload.get("summary", "")
    source_type = normalize_choice(payload.get("source_type"), SOURCE_TYPES, "other")
    topics = normalize_list(payload.get("topics"))
    claims = extract_claim_candidates(payload)
    evidence_level = estimate_evidence_level(payload)

    combined_text = " ".join([
        str(title),
        str(summary),
        " ".join(claims),
        " ".join(topics),
    ])

    hype_flags = detect_hype_flags(combined_text)
    topic_risks = detect_topic_risks(combined_text, topics)
    risk_flags = sorted(set(hype_flags + topic_risks))

    signal_score = calculate_signal_score(payload, evidence_level, risk_flags)
    route = recommend_route(payload, signal_score, evidence_level, risk_flags)
    verification_plan = build_verification_plan(evidence_level, claims, source_type, risk_flags)

    mission_candidate = build_mission_candidate(payload, claims, route)
    doctrine_candidate = build_doctrine_candidate(payload, claims, route)

    return {
        "module": "intelligence_intake_triage_v1",
        "title": title,
        "source_type": source_type,
        "topics": topics,
        "claims": claims,
        "evidence_level": evidence_level,
        "signal_score": signal_score,
        "risk_flags": risk_flags,
        "triage": route,
        "verification_plan": verification_plan,
        "mission_candidate": mission_candidate,
        "doctrine_candidate": doctrine_candidate,
        "next_action": build_next_action(route, verification_plan),
        "doctrine": (
            "Raw information does not become action until it is classified, verified, routed, "
            "and converted into a mission, doctrine candidate, or parking-lot item."
        ),
    }


def build_next_action(route: Dict[str, Any], verification_plan: List[str]) -> str:
    recommendation = route["recommendation"]
    destination = route["recommended_route"]

    if recommendation == "CONVERT_TO_MISSION":
        return "Create a Mission Execution record from the mission_candidate."

    if recommendation == "CONVERT_TO_DOCTRINE_CANDIDATE":
        return "Create a Doctrine Registry record from the doctrine_candidate."

    if recommendation == "VERIFY_FIRST":
        return verification_plan[0] if verification_plan else "Verify before using."

    if recommendation == "DISCARD":
        return "Discard or archive. Do not spend execution time."

    if destination == "curiosity_parking_lot":
        return "Park for later. Do not let this interrupt current missions."

    return f"Route to {destination} for further review."


def batch_triage(payload: Dict[str, Any]) -> Dict[str, Any]:
    items = payload.get("items", [])

    results = []
    for item in items:
        if isinstance(item, dict):
            results.append(triage_intelligence(item))

    counts = {
        "USE_NOW": 0,
        "VERIFY_FIRST": 0,
        "PARK": 0,
        "DISCARD": 0,
        "CONVERT_TO_MISSION": 0,
        "CONVERT_TO_DOCTRINE_CANDIDATE": 0,
    }

    for result in results:
        rec = result["triage"]["recommendation"]
        if rec in counts:
            counts[rec] += 1

    return {
        "module": "intelligence_intake_batch_triage_v1",
        "count": len(results),
        "recommendation_counts": counts,
        "results": results,
        "next_action": build_batch_next_action(counts),
    }


def build_batch_next_action(counts: Dict[str, int]) -> str:
    if counts["CONVERT_TO_MISSION"] > 0:
        return "Create missions from the highest-signal mission candidates."

    if counts["VERIFY_FIRST"] > 0:
        return "Verify the highest-risk claims before action."

    if counts["CONVERT_TO_DOCTRINE_CANDIDATE"] > 0:
        return "Review doctrine candidates before promotion."

    return "Park or discard low-signal items and return to active missions."
