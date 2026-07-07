from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend import mission_control_service as service


def run_record(workflow: str, raw: bool = False) -> int:
    entry = service.record_daily_driver_log_entry(workflow=workflow)
    print(f"Recorded daily driver log: {entry.get('workflow')} @ {entry.get('created_at')}")

    if raw:
        print(json.dumps(entry, indent=2))

    return 0 if entry.get("status") == "ok" else 1


def run_recent(limit: int = 10, raw: bool = False) -> int:
    state = service.get_daily_driver_log_state(limit=limit)

    print("\nPROJECT SALUS — RECENT DAILY LOGS")
    print("=" * 40)
    print(f"Path: {state['path']}")
    print(f"Returned: {state['counts']['returned']}")

    for entry in state["entries"]:
        print(f"- {entry.get('created_at')} | {entry.get('workflow')} | {entry.get('status')}")

    if raw:
        print("\nRaw JSON:")
        print(json.dumps(state, indent=2))

    return 0


def run_state(raw: bool = False) -> int:
    state = service.get_daily_driver_log_state(limit=20)

    print("\nPROJECT SALUS — DAILY LOG STATE")
    print("=" * 38)
    print(f"Path: {state['path']}")
    print(f"Returned: {state['counts']['returned']}")
    print(f"Health Logs: {state['counts']['health']}")
    print(f"Start Logs: {state['counts']['start_my_day']}")
    print(f"End Logs: {state['counts']['end_my_day']}")
    print(f"Recommended Action: {state['recommended_action']}")

    if raw:
        print("\nRaw JSON:")
        print(json.dumps(state, indent=2))

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Project Salus daily log launcher.")
    parser.add_argument(
        "command",
        choices=["record-health", "record-start", "record-end", "recent", "state"],
    )
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--raw", action="store_true")

    args = parser.parse_args()

    if args.command == "record-health":
        return run_record("health", raw=args.raw)
    if args.command == "record-start":
        return run_record("start_my_day", raw=args.raw)
    if args.command == "record-end":
        return run_record("end_my_day", raw=args.raw)
    if args.command == "recent":
        return run_recent(limit=args.limit, raw=args.raw)
    if args.command == "state":
        return run_state(raw=args.raw)

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
