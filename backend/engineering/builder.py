from datetime import datetime

SALUS_ENGINEERING_TEAM = [
    {
        "name": "Chief Architect",
        "mission": "Design scalable Project Salus architecture and prevent technical debt.",
        "status": "active",
    },
    {
        "name": "Backend Engineer",
        "mission": "Build FastAPI services, APIs, and database logic.",
        "status": "active",
    },
    {
        "name": "Frontend Engineer",
        "mission": "Build Mission Control interfaces and user workflows.",
        "status": "active",
    },
    {
        "name": "Security Engineer",
        "mission": "Protect Project Salus with authentication, authorization, logging, and secure defaults.",
        "status": "active",
    },
    {
        "name": "QA Engineer",
        "mission": "Create tests, detect regressions, and verify release readiness.",
        "status": "active",
    },
    {
        "name": "Documentation Engineer",
        "mission": "Maintain changelogs, architecture notes, and developer instructions.",
        "status": "active",
    },
    {
        "name": "Legacy Architect",
        "mission": "Ensure every major feature supports the Barney Legacy Protocol.",
        "status": "active",
    },
]

ARCHITECTURE_RULES = [
    "Every feature must improve judgment or execution.",
    "Every feature must be modular, testable, replaceable, and observable.",
    "Every major decision must consider security, freedom, and legacy impact.",
    "Prefer compounding infrastructure over isolated features.",
    "Do not create technical debt without documenting why.",
]

def get_builder_status():
    return {
        "system": "Salus Engineering Platform",
        "version": "0.4.0",
        "status": "operational",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "team": SALUS_ENGINEERING_TEAM,
        "rules": ARCHITECTURE_RULES,
    }

