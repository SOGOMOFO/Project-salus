from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend import mission_control_service as service


def main() -> int:
    state = service.get_end_my_day_workflow_state()

    print("\nPROJECT SALUS — END MY DAY AAR")
    print("=" * 40)
    print(f"Daily Use Ready: {state['daily_use_ready']}")
    print(f"Health Status: {state['health_status']}")
    print(f"Closeout Intent: {state['commander_closeout_intent']}")

    print("\nAAR Questions:")
    for index, question in enumerate(state["aar_questions"], start=1):
        print(f"{index}. {question}")

    print("\nCarry-Forward Candidates:")
    for item in state["carry_forward_candidates"]:
        print(f"- {item['item']}")

    print("\nRisk Review:")
    for risk in state["risk_review"]:
        print(f"- {risk}")

    print("\nRaw JSON:")
    print(json.dumps(state, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
