from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend import mission_control_service as service


def print_header(title: str) -> None:
    print()
    print(title)
    print("=" * len(title))


def print_health(state: dict[str, Any], raw: bool = False) -> None:
    print_header("PROJECT SALUS — DAILY DRIVER HEALTH")
    print(f"Status: {state['status']}")
    print(f"Daily Use Ready: {state['daily_use_ready']}")
    print(f"Recommended Action: {state['recommended_action']}")

    print("\nComponents:")
    for item in state["components"]:
        print(f"- {item['name']}: {item['status']} — {item['detail']}")

    if raw:
        print("\nRaw JSON:")
        print(json.dumps(state, indent=2))


def print_start(state: dict[str, Any], raw: bool = False) -> None:
    print_header("PROJECT SALUS — START MY DAY")
    print(f"Daily Use Ready: {state['daily_use_ready']}")
    print(f"Health Status: {state['health_status']}")
    print(f"Commander Intent: {state['commander_intent']}")

    print("\nMission Focus:")
    focus = state["mission_focus"]
    print(f"- Primary: {focus['primary']}")
    print(f"- Secondary: {focus['secondary']}")
    print(f"- Constraint: {focus['constraint']}")

    print("\nTop Actions:")
    for index, action in enumerate(state["top_actions"], start=1):
        print(f"{index}. {action}")

    print("\nTop Risks:")
    for risk in state["top_risks"]:
        print(f"- {risk}")

    print("\nEnd-of-Day AAR Questions:")
    for question in state["end_of_day_aar_prompt"]["questions"]:
        print(f"- {question}")

    if raw:
        print("\nRaw JSON:")
        print(json.dumps(state, indent=2))


def print_end(state: dict[str, Any], raw: bool = False) -> None:
    print_header("PROJECT SALUS — END MY DAY AAR")
    print(f"Daily Use Ready: {state['daily_use_ready']}")
    print(f"Health Status: {state['health_status']}")
    print(f"Closeout Intent: {state['commander_closeout_intent']}")

    print("\nAAR Questions:")
    for index, question in enumerate(state["aar_questions"], start=1):
        print(f"{index}. {question}")

    print("\nCarry-Forward Candidates:")
    for item in state["carry_forward_candidates"]:
        print(f"- {item['item']}")

    print("\nTomorrow Setup:")
    setup = state["tomorrow_setup"]
    print(f"- First Action: {setup['recommended_first_action']}")
    print(f"- Review: {setup['recommended_review']}")
    print(f"- Constraint: {setup['constraint']}")

    if raw:
        print("\nRaw JSON:")
        print(json.dumps(state, indent=2))


def run_health(raw: bool = False) -> int:
    state = service.get_daily_driver_health_state()
    print_health(state, raw=raw)
    return 0 if state.get("daily_use_ready") else 1


def run_start(raw: bool = False) -> int:
    state = service.get_start_my_day_workflow_state()
    print_start(state, raw=raw)
    return 0


def run_end(raw: bool = False) -> int:
    state = service.get_end_my_day_workflow_state()
    print_end(state, raw=raw)
    return 0


def run_all(raw: bool = False) -> int:
    health = service.get_daily_driver_health_state()
    start = service.get_start_my_day_workflow_state()
    end = service.get_end_my_day_workflow_state()

    print_health(health, raw=False)
    print_start(start, raw=False)
    print_end(end, raw=False)

    if raw:
        print("\nFULL RAW JSON:")
        print(json.dumps(
            {
                "health": health,
                "start_my_day": start,
                "end_my_day": end,
            },
            indent=2,
        ))

    return 0 if health.get("daily_use_ready") else 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Project Salus daily driver command launcher."
    )
    parser.add_argument(
        "command",
        choices=["health", "start", "end", "all"],
        help="Daily driver command to run.",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print raw JSON output.",
    )

    args = parser.parse_args()

    if args.command == "health":
        return run_health(raw=args.raw)
    if args.command == "start":
        return run_start(raw=args.raw)
    if args.command == "end":
        return run_end(raw=args.raw)
    if args.command == "all":
        return run_all(raw=args.raw)

    parser.print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
