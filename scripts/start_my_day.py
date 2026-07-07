from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend import mission_control_service as service


def main() -> int:
    state = service.get_start_my_day_workflow_state()

    print("\nPROJECT SALUS — START MY DAY")
    print("=" * 38)
    print(f"Daily Use Ready: {state['daily_use_ready']}")
    print(f"Health Status: {state['health_status']}")
    print(f"Commander Intent: {state['commander_intent']}")

    print("\nTop Actions:")
    for index, action in enumerate(state["top_actions"], start=1):
        print(f"{index}. {action}")

    print("\nTop Risks:")
    for risk in state["top_risks"]:
        print(f"- {risk}")

    print("\nEnd-of-Day AAR Questions:")
    for question in state["end_of_day_aar_prompt"]["questions"]:
        print(f"- {question}")

    print("\nRaw JSON:")
    print(json.dumps(state, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
