from pathlib import Path
from typing import Any, Dict, List


BUILD_ACCELERATOR_DOCTRINE = (
    "Build faster by sequencing work, reducing manual decision friction, checking system map status, "
    "and converting priorities into tested, committable build blocks."
)

CORE_MODULES = [
    {
        "key": "decision_firewall",
        "name": "Decision Firewall",
        "service": "backend/services/decision_firewall_service.py",
        "route": "backend/routes/decision_firewall.py",
        "test": "tests/test_decision_firewall_api.py",
        "purpose": "Filter ideas by evidence, fit, ROI, risk, and opportunity cost.",
    },
    {
        "key": "ai_governance",
        "name": "AI Governance Checklist",
        "service": "backend/services/ai_governance_service.py",
        "route": "backend/routes/ai_governance.py",
        "test": "tests/test_ai_governance_api.py",
        "purpose": "Control AI tool and agent risk before deployment.",
    },
    {
        "key": "wealth_os",
        "name": "Wealth Operating System",
        "service": "backend/services/wealth_os_service.py",
        "route": "backend/routes/wealth_os.py",
        "test": "tests/test_wealth_os_api.py",
        "purpose": "Assign every dollar a mission.",
    },
    {
        "key": "echo_seven_assessment",
        "name": "Echo Seven Assessment Package",
        "service": "backend/services/echo_seven_assessment_service.py",
        "route": "backend/routes/echo_seven_assessment.py",
        "test": "tests/test_echo_seven_assessment_api.py",
        "purpose": "Productize AI Governance & Cyber Readiness as a sellable offer.",
    },
    {
        "key": "daily_brief_v2",
        "name": "Daily Commander Brief V2",
        "service": "backend/services/daily_brief_service.py",
        "route": "backend/routes/daily_brief.py",
        "test": "tests/test_daily_brief_v2_api.py",
        "purpose": "Convert risks and priorities into a daily action brief.",
    },
    {
        "key": "strategy_critical_thinking",
        "name": "Strategy & Critical Thinking Directorate",
        "service": "backend/services/strategy_critical_thinking_service.py",
        "route": "backend/routes/strategy_critical_thinking.py",
        "test": "tests/test_strategy_critical_thinking_api.py",
        "purpose": "Run assumption checks, red-team analysis, effects forecasts, and decision memos.",
    },
    {
        "key": "mission_execution",
        "name": "Mission Execution Engine",
        "service": "backend/services/mission_execution_service.py",
        "route": "backend/routes/mission_execution.py",
        "test": "tests/test_mission_execution_api.py",
        "purpose": "Turn recommendations into missions, status updates, sprints, and AARs.",
    },
    {
        "key": "mission_registry",
        "name": "Mission Registry & Persistence",
        "service": "backend/services/mission_registry_service.py",
        "route": "backend/routes/mission_registry.py",
        "test": "tests/test_mission_registry_api.py",
        "purpose": "Persist missions, blockers, status, and AAR history.",
    },
    {
        "key": "command_center",
        "name": "Command Center Orchestrator",
        "service": "backend/services/command_center_service.py",
        "route": "backend/routes/command_center.py",
        "test": "tests/test_command_center_api.py",
        "purpose": "Unify readiness, risks, blocked missions, and priority actions.",
    },
    {
        "key": "doctrine_registry",
        "name": "Doctrine Registry & Learning Loop",
        "service": "backend/services/doctrine_registry_service.py",
        "route": "backend/routes/doctrine_registry.py",
        "test": "tests/test_doctrine_registry_api.py",
        "purpose": "Turn lessons into doctrine candidates and active operating rules.",
    },
    {
        "key": "intelligence_intake",
        "name": "Intelligence Intake & Triage",
        "service": "backend/services/intelligence_intake_service.py",
        "route": "backend/routes/intelligence_intake.py",
        "test": "tests/test_intelligence_intake_api.py",
        "purpose": "Classify videos, claims, ideas, and notes before action.",
    },
    {
        "key": "curiosity_parking_lot",
        "name": "Curiosity Parking Lot & Backlog",
        "service": "backend/services/curiosity_parking_lot_service.py",
        "route": "backend/routes/curiosity_parking_lot.py",
        "test": "tests/test_curiosity_parking_lot_api.py",
        "purpose": "Store, review, promote, or discard low-certainty ideas.",
    },
    {
        "key": "workflow_orchestrator",
        "name": "Workflow Orchestrator",
        "service": "backend/services/workflow_orchestrator_service.py",
        "route": "backend/routes/workflow_orchestrator.py",
        "test": "tests/test_workflow_orchestrator_api.py",
        "purpose": "Move intake through triage into mission, doctrine, parking, or discard.",
    },
    {
        "key": "build_accelerator",
        "name": "Build Accelerator & System Map",
        "service": "backend/services/build_accelerator_service.py",
        "route": "backend/routes/build_accelerator.py",
        "test": "tests/test_build_accelerator_api.py",
        "purpose": "Map build status, select next build, create sprints, and generate release checks.",
    },
]


NEXT_BUILD_CANDIDATES = [
    {
        "key": "operator_console",
        "name": "Operator Console V1",
        "strategic_fit": 10,
        "roi": 9,
        "difficulty": 6,
        "risk": 4,
        "purpose": "Give Kyle one command-facing console for modules, missions, risks, and next actions.",
        "why_next": "Backend capability is outpacing visibility.",
    },
    {
        "key": "client_delivery_pack",
        "name": "Echo Seven Client Delivery Pack V1",
        "strategic_fit": 10,
        "roi": 9,
        "difficulty": 5,
        "risk": 3,
        "purpose": "Generate assessment reports, executive summaries, risk matrices, and implementation plans.",
        "why_next": "Turns Echo Seven into a sellable client delivery system.",
    },
    {
        "key": "federal_contracting_hub",
        "name": "Federal Contracting Hub V1",
        "strategic_fit": 9,
        "roi": 9,
        "difficulty": 7,
        "risk": 5,
        "purpose": "Track opportunities, NAICS, capture steps, readiness, and bid/no-bid decisions.",
        "why_next": "Directly supports Echo Seven federal-contracting path.",
    },
    {
        "key": "connector_registry",
        "name": "Connector Registry V1",
        "strategic_fit": 9,
        "roi": 8,
        "difficulty": 8,
        "risk": 7,
        "purpose": "Inventory external connectors, permissions, data access, sync status, and risk.",
        "why_next": "Connectors are core Salus architecture and need governance.",
    },
    {
        "key": "auth_identity_access",
        "name": "Identity & Access Control V1",
        "strategic_fit": 10,
        "roi": 8,
        "difficulty": 8,
        "risk": 7,
        "purpose": "Add users, roles, permissions, and access boundaries.",
        "why_next": "Required before family-user or client-facing use.",
    },
    {
        "key": "database_migration",
        "name": "Database Migration V1",
        "strategic_fit": 9,
        "roi": 8,
        "difficulty": 8,
        "risk": 6,
        "purpose": "Move persistent JSON storage toward database-backed persistence.",
        "why_next": "Needed before serious multi-user or production use.",
    },
    {
        "key": "frontend_dashboard",
        "name": "Frontend Dashboard Upgrade V1",
        "strategic_fit": 8,
        "roi": 8,
        "difficulty": 7,
        "risk": 4,
        "purpose": "Expose Command Center, missions, workflows, and modules in the browser.",
        "why_next": "Backend capability needs better usability.",
    },
]


def path_exists(path: str) -> bool:
    return Path(path).exists()


def clamp_int(value: Any, minimum: int, maximum: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        number = minimum

    return max(minimum, min(number, maximum))


def module_status(module: Dict[str, str]) -> Dict[str, Any]:
    service_exists = path_exists(module["service"])
    route_exists = path_exists(module["route"])
    test_exists = path_exists(module["test"])

    completion = round(
        (int(service_exists) + int(route_exists) + int(test_exists)) / 3 * 100
    )

    if completion == 100:
        status = "implemented"
    elif completion > 0:
        status = "partial"
    else:
        status = "missing"

    return {
        **module,
        "service_exists": service_exists,
        "route_exists": route_exists,
        "test_exists": test_exists,
        "completion": completion,
        "status": status,
    }


def build_system_map() -> Dict[str, Any]:
    modules = [module_status(module) for module in CORE_MODULES]

    implemented = [module for module in modules if module["status"] == "implemented"]
    partial = [module for module in modules if module["status"] == "partial"]
    missing = [module for module in modules if module["status"] == "missing"]

    completion_score = round(
        sum(module["completion"] for module in modules) / len(modules)
    ) if modules else 0

    return {
        "module": "build_accelerator_system_map",
        "total_modules": len(modules),
        "implemented_count": len(implemented),
        "partial_count": len(partial),
        "missing_count": len(missing),
        "completion_score": completion_score,
        "modules": modules,
        "risk_flags": build_system_risk_flags(partial, missing),
        "next_action": (
            "Fix partial modules before adding more build surface."
            if partial
            else "Proceed to next high-leverage build block."
        ),
        "doctrine": BUILD_ACCELERATOR_DOCTRINE,
    }


def build_system_risk_flags(partial: List[Dict[str, Any]], missing: List[Dict[str, Any]]) -> List[str]:
    flags: List[str] = []

    if partial:
        flags.append("Partial modules detected; service/route/test mismatch may break imports or coverage.")

    if missing:
        flags.append("Some expected modules are missing.")

    if not partial and not missing:
        flags.append("Core module map appears complete.")

    return flags


def candidate_score(candidate: Dict[str, Any], focus: str) -> int:
    strategic_fit = int(candidate.get("strategic_fit", 5))
    roi = int(candidate.get("roi", 5))
    difficulty = int(candidate.get("difficulty", 5))
    risk = int(candidate.get("risk", 5))

    lowered = focus.lower()
    focus_bonus = 0

    if lowered:
        searchable = " ".join([
            candidate["key"],
            candidate["name"],
            candidate["purpose"],
            candidate["why_next"],
        ]).lower()

        if lowered in searchable:
            focus_bonus = 15

    score = round(
        strategic_fit * 10 * 0.35
        + roi * 10 * 0.30
        + (10 - difficulty) * 10 * 0.15
        + (10 - risk) * 10 * 0.10
        + 50 * 0.10
        + focus_bonus
    )

    return max(0, min(score, 100))


def build_scope(candidate: Dict[str, Any]) -> List[str]:
    key = candidate["key"]

    if key == "operator_console":
        return [
            "Command Center summary endpoint",
            "Module map display",
            "Top mission display",
            "Risk flags display",
            "Next action display",
        ]

    if key == "client_delivery_pack":
        return [
            "Assessment summary generator",
            "Executive report structure",
            "Risk matrix output",
            "Implementation roadmap output",
            "Copy-paste client deliverable",
        ]

    if key == "federal_contracting_hub":
        return [
            "Opportunity record",
            "Bid/no-bid scoring",
            "NAICS tracking",
            "Capture checklist",
            "Contracting dashboard",
        ]

    if key == "connector_registry":
        return [
            "Connector inventory",
            "Permission model",
            "Data type exposure",
            "Sync status",
            "Connector risk dashboard",
        ]

    return [
        "Framework endpoint",
        "Core service logic",
        "API route",
        "Tests",
        "Commit and push",
    ]


def build_success_criteria(candidate: Dict[str, Any]) -> List[str]:
    return [
        f"{candidate['name']} framework endpoint returns 200.",
        f"{candidate['name']} core logic has API tests.",
        "Full pytest suite passes.",
        "Git working tree is clean after commit and push.",
    ]


def recommend_next_build(payload: Dict[str, Any]) -> Dict[str, Any]:
    focus = str(payload.get("focus", "") or "")
    capacity = clamp_int(payload.get("capacity", 3), 1, 10)
    system_map = build_system_map()

    candidates = []
    for candidate in NEXT_BUILD_CANDIDATES:
        scored = dict(candidate)
        scored["build_score"] = candidate_score(candidate, focus)
        scored["recommended_scope"] = build_scope(candidate)
        scored["success_criteria"] = build_success_criteria(candidate)
        candidates.append(scored)

    candidates = sorted(candidates, key=lambda item: item["build_score"], reverse=True)

    blockers = []
    if system_map["partial_count"] > 0:
        blockers.append("Partial modules should be repaired before large new features.")

    return {
        "module": "build_accelerator_next_build",
        "focus": focus,
        "capacity": capacity,
        "top_recommendations": candidates[:capacity],
        "all_candidates": candidates,
        "blockers": blockers,
        "next_action": (
            "Repair partial modules first."
            if blockers
            else f"Build next module: {candidates[0]['name']}"
        ),
        "doctrine": "Choose the next build by strategic fit, ROI, difficulty, risk, and current bottleneck.",
    }


def build_release_checklist(payload: Dict[str, Any]) -> Dict[str, Any]:
    changed_files = payload.get("changed_files", [])
    if not isinstance(changed_files, list):
        changed_files = []

    commands = [
        "python3 -m py_compile backend/main.py",
        "pytest -q",
        "git status",
    ]

    if changed_files:
        commands.insert(0, "python3 -m py_compile " + " ".join(changed_files))

    return {
        "module": "build_accelerator_release_checklist",
        "required_checks": [
            "Relevant files compile.",
            "Targeted tests pass.",
            "Full pytest suite passes.",
            "No unexpected untracked files.",
            "Commit message describes the module.",
            "Push completes.",
            "Working tree is clean.",
        ],
        "commands": commands,
        "commit_template": 'git add <files> && git commit -m "add <module name>" && git push && git status',
        "stop_conditions": [
            "Any py_compile failure.",
            "Any pytest failure.",
            "Unexpected route collision.",
            "Untracked files not intentionally included.",
        ],
    }


def build_sprint(payload: Dict[str, Any]) -> Dict[str, Any]:
    focus = str(payload.get("focus", "") or "")
    capacity = clamp_int(payload.get("capacity", 3), 1, 7)
    include_release_checklist = bool(payload.get("include_release_checklist", True))

    next_build = recommend_next_build({"focus": focus, "capacity": capacity})
    selected = next_build["top_recommendations"][:capacity]

    tasks = []
    for index, item in enumerate(selected, start=1):
        tasks.append({
            "sequence": index,
            "module_key": item["key"],
            "module_name": item["name"],
            "purpose": item["purpose"],
            "build_score": item["build_score"],
            "scope": item["recommended_scope"],
            "success_criteria": item["success_criteria"],
        })

    return {
        "module": "build_accelerator_sprint",
        "sprint_name": payload.get("sprint_name", "Salus Build Sprint"),
        "focus": focus,
        "capacity": capacity,
        "tasks": tasks,
        "release_checklist": build_release_checklist({}) if include_release_checklist else {},
        "next_action": f"Start with {tasks[0]['module_name']}." if tasks else "No build tasks selected.",
        "doctrine": "A build sprint should produce tested, committed, pushed increments.",
    }


def build_smoke_test_plan(payload: Dict[str, Any]) -> Dict[str, Any]:
    include_optional = bool(payload.get("include_optional", True))

    endpoints = [
        "/build-accelerator/framework",
        "/build-accelerator/system-map",
        "/build-accelerator/next-build",
        "/command-center/framework",
        "/mission-registry/framework",
        "/doctrine-registry/framework",
        "/intelligence-intake/framework",
    ]

    if include_optional:
        endpoints.extend([
            "/curiosity-parking-lot/framework",
            "/workflow-orchestrator/framework",
            "/strategy-critical-thinking/framework",
            "/ai-governance/framework",
            "/wealth-os/framework",
            "/echo-seven/assessment/framework",
        ])

    return {
        "module": "build_accelerator_smoke_test_plan",
        "purpose": "Quickly verify high-value API surfaces after builds.",
        "endpoints": endpoints,
        "terminal_commands": [
            "python3 -m backend.main",
            "# In another terminal, test endpoints with curl or browser.",
            "pytest -q",
        ],
        "pass_condition": "Framework endpoints return HTTP 200 and full pytest suite passes.",
    }


def build_commit_pack(payload: Dict[str, Any]) -> Dict[str, Any]:
    files = payload.get("files", [])
    message = str(payload.get("message", "add build accelerator module")).strip()

    if not isinstance(files, list):
        files = []

    file_string = " ".join(files) if files else "<files>"

    return {
        "module": "build_accelerator_commit_pack",
        "files": files,
        "message": message,
        "commands": [
            "git status",
            f"git add {file_string}",
            f'git commit -m "{message}"',
            "git push",
            "git status",
        ],
        "doctrine": "Save only after tests pass. Clean checkpoints beat speed without control.",
    }
