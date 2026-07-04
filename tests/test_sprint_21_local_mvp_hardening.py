import importlib.util
from pathlib import Path


def load_audit_module():
    spec = importlib.util.spec_from_file_location("salus_audit", "scripts/salus_audit.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sprint_21_audit_script_exists():
    assert Path("scripts/salus_audit.py").exists()


def test_sprint_21_audit_collects_routes():
    module = load_audit_module()
    routes = module.collect_routes("backend/main.py")
    paths = {route["path"] for route in routes}

    assert "/command/dashboard-index" in paths
    assert "/api/command/dashboard-index" in paths
    assert "/command/readiness" in paths
    assert "/api/command/readiness" in paths
    assert "/command/workflows" in paths


def test_sprint_21_audit_builds_inventory():
    module = load_audit_module()
    inventory = module.build_inventory("backend/main.py")

    assert inventory["status"] == "ok"
    assert inventory["module"] == "local_mvp_hardening_audit"
    assert inventory["route_count"] >= 20
    assert inventory["sprint_marker_count"] >= 10
    assert "metrics" in inventory
    assert inventory["metrics"]["line_count"] > 0


def test_sprint_21_hardening_docs_exist():
    required = [
        "docs/SPRINT_21_ROUTE_INVENTORY.md",
        "docs/SPRINT_21_TECHNICAL_DEBT_REGISTER.md",
        "docs/SPRINT_21_MODULE_SPLIT_PLAN.md",
        "docs/SPRINT_21_DATA_STORAGE_PLAN.md",
        "docs/SPRINT_21_RISK_REGISTER.md",
        "docs/salus_audit_inventory.json",
    ]

    for path in required:
        assert Path(path).exists(), path
