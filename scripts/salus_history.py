from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend import mission_control_service as service


def run_recent(limit: int = 10, raw: bool = False) -> int:
    state = service.get_daily_driver_history_view(limit=limit)

    print("\nPROJECT SALUS — DAILY HISTORY")
    print("=" * 38)
    print(f"Returned: {len(state['entries'])}")

    for entry in state["entries"]:
        print(
            f"- {entry.get('created_at')} | "
            f"{entry.get('workflow')} | "
            f"{entry.get('status')} | "
            f"ready={entry.get('daily_use_ready')}"
        )

    if raw:
        print("\nRaw JSON:")
        print(json.dumps(state, indent=2))

    return 0


def run_last(workflow: str, raw: bool = False) -> int:
    state = service.get_last_daily_driver_log_entry(workflow)

    print(f"\nPROJECT SALUS — LAST {workflow.upper()} LOG")
    print("=" * 42)

    if not state.get("found"):
        print("No matching log found.")
        return 1

    entry = state["entry"]
    print(f"Created At: {entry.get('created_at')}")
    print(f"Workflow: {entry.get('workflow')}")
    print(f"Status: {entry.get('status')}")

    if raw:
        print("\nRaw JSON:")
        print(json.dumps(state, indent=2))

    return 0


def run_last_aar(raw: bool = False) -> int:
    state = service.get_last_end_my_day_aar_summary()

    print("\nPROJECT SALUS — LAST END MY DAY AAR")
    print("=" * 42)

    if not state.get("found"):
        print("No End My Day AAR log found.")
        print(state.get("recommended_action"))
        return 1

    print(f"Created At: {state.get('created_at')}")
    print(f"Health Status: {state.get('health_status')}")
    print(f"Daily Use Ready: {state.get('daily_use_ready')}")

    print("\nCarry Forward:")
    for item in state.get("carry_forward_candidates", []):
        print(f"- {item.get('item')}")

    if raw:
        print("\nRaw JSON:")
        print(json.dumps(state, indent=2))

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Salus daily history viewer.")
    parser.add_argument("command", choices=["recent", "last-health", "last-start", "last-end", "last-aar"])
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--raw", action="store_true")

    args = parser.parse_args()

    if args.command == "recent":
        return run_recent(limit=args.limit, raw=args.raw)
    if args.command == "last-health":
        return run_last("health", raw=args.raw)
    if args.command == "last-start":
        return run_last("start_my_day", raw=args.raw)
    if args.command == "last-end":
        return run_last("end_my_day", raw=args.raw)
    if args.command == "last-aar":
        return run_last_aar(raw=args.raw)

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
