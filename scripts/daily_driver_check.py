from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend import mission_control_service as service


def main() -> int:
    state = service.get_daily_driver_health_state()

    print("\nPROJECT SALUS DAILY DRIVER HEALTH")
    print("=" * 42)
    print(f"Status: {state['status']}")
    print(f"Daily Use Ready: {state['daily_use_ready']}")
    print(f"Recommended Action: {state['recommended_action']}")
    print("\nComponents:")

    for item in state["components"]:
        print(f"- {item['name']}: {item['status']} — {item['detail']}")

    print("\nRaw JSON:")
    print(json.dumps(state, indent=2))

    return 0 if state["daily_use_ready"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
