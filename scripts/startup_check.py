from __future__ import annotations

import os
import sys
from pathlib import Path


REQUIRED_FILES = [
    "backend/main.py",
    "backend/mission_control_service.py",
    "backend/mission_control_views.py",
    "run_praevale.sh",
]

REQUIRED_ROUTES = [
    "/api/mission-control/local-file-intelligence",
    "/mission-control/v1",
    "/mission-control/login",
    "/api/mission-control/dashboard",
    "/api/mission-control/mvp-readiness",
    "/api/mission-control/auth/status",
    "/api/mission-control/background-jobs",
    "/api/mission-control/model-providers",
    "/api/mission-control/tool-adapters",
    "/api/mission-control/firewall",
    "/api/mission-control/connectors",
    "/api/mission-control/agent-runtime",
]


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    sys.exit(1)


def main() -> None:
    root = Path(".").resolve()

    for file_path in REQUIRED_FILES:
        if not (root / file_path).exists():
            fail(f"Missing required file: {file_path}")

    try:
        from backend.main import app
        from backend import mission_control_service as service
    except Exception as exc:
        fail(f"Import failed: {exc}")

    routes = service.get_route_inventory(app)
    route_paths = {route["path"] for route in routes}

    missing = [path for path in REQUIRED_ROUTES if path not in route_paths]
    if missing:
        fail(f"Missing required routes: {missing}")

    auth_state = service.get_local_auth_state()
    readiness = service.get_local_mvp_readiness()

    print("Project Salus startup check")
    print(f"Root: {root}")
    print(f"Environment: {os.getenv('SALUS_ENV', 'local')}")
    print(f"Auth: {auth_state.get('status')}")
    print(f"Readiness: {readiness.get('status')}")
    print(f"Routes checked: {len(REQUIRED_ROUTES)}")
    print("OK")


if __name__ == "__main__":
    main()
