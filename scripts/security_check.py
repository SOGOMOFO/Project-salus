from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.main import app
from backend import mission_control_service as service


def main() -> None:
    state = service.get_security_hardening_state(app)

    print("Project Salus security hardening check")
    print(f"Status: {state.get('status')}")
    print(f"Environment: {state.get('environment')}")
    print(f"Auth enabled: {state.get('auth_enabled')}")
    print(f"Default password active: {state.get('default_password_active')}")
    print(f"External actions allowed: {state.get('external_actions_allowed')}")
    print(f"Model external calls allowed: {state.get('model_external_calls_allowed')}")
    print(f"Connector writes allowed: {state.get('connector_writes_allowed')}")

    warnings = state.get("warnings", [])
    blockers = state.get("blockers", [])

    if warnings:
        print(f"Warnings: {warnings}")

    if blockers:
        print(f"Blockers: {blockers}")
        sys.exit(1)

    print("OK")


if __name__ == "__main__":
    main()
