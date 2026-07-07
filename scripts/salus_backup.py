from __future__ import annotations

import argparse
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BACKUP_ROOT = ROOT / "backups"

BACKUP_TARGETS = [
    "data/daily_driver_logs.jsonl",
    "backend/mission_control_service.py",
    "backend/main.py",
    "scripts/salus_day.py",
    "scripts/salus_log.py",
    "scripts/salus_history.py",
    "scripts/daily_driver_check.py",
    "scripts/start_my_day.py",
    "scripts/end_my_day.py",
    "tests/test_phase_3_daily_driver_health.py",
    "tests/test_phase_3_start_my_day_workflow.py",
    "tests/test_phase_3_end_my_day_workflow.py",
    "tests/test_phase_3_daily_driver_command_launcher.py",
    "tests/test_phase_3_daily_log_persistence.py",
    "tests/test_phase_3_daily_log_viewer.py",
]


def utc_stamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def copy_target(target: str, dest_root: Path) -> dict:
    source = ROOT / target
    destination = dest_root / target

    if not source.exists():
        return {
            "target": target,
            "status": "missing",
            "source": str(source),
            "destination": str(destination),
        }

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)

    return {
        "target": target,
        "status": "copied",
        "source": str(source),
        "destination": str(destination),
        "bytes": destination.stat().st_size,
    }


def create_snapshot(raw: bool = False) -> int:
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)

    dest_root = BACKUP_ROOT / f"daily_driver_snapshot_{utc_stamp()}"
    dest_root.mkdir(parents=True, exist_ok=True)

    results = [copy_target(target, dest_root) for target in BACKUP_TARGETS]

    manifest = {
        "status": "ok",
        "snapshot": dest_root.name,
        "path": str(dest_root),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "targets": len(results),
            "copied": len([item for item in results if item["status"] == "copied"]),
            "missing": len([item for item in results if item["status"] == "missing"]),
        },
        "results": results,
    }

    (dest_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )

    print("\nPROJECT SALUS — DAILY DRIVER SNAPSHOT")
    print("=" * 43)
    print(f"Snapshot: {manifest['snapshot']}")
    print(f"Path: {manifest['path']}")
    print(f"Copied: {manifest['counts']['copied']}")
    print(f"Missing: {manifest['counts']['missing']}")

    if raw:
        print("\nRaw JSON:")
        print(json.dumps(manifest, indent=2))

    return 0


def list_snapshots(raw: bool = False) -> int:
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)

    snapshots = sorted(
        [
            path
            for path in BACKUP_ROOT.iterdir()
            if path.is_dir() and path.name.startswith("daily_driver_snapshot_")
        ],
        reverse=True,
    )

    data = {
        "status": "ok",
        "count": len(snapshots),
        "snapshots": [str(path) for path in snapshots],
    }

    print("\nPROJECT SALUS — BACKUP SNAPSHOTS")
    print("=" * 39)

    if not snapshots:
        print("No snapshots found.")
    else:
        for path in snapshots:
            print(f"- {path}")

    if raw:
        print("\nRaw JSON:")
        print(json.dumps(data, indent=2))

    return 0


def latest_snapshot(raw: bool = False) -> int:
    BACKUP_ROOT.mkdir(parents=True, exist_ok=True)

    snapshots = sorted(
        [
            path
            for path in BACKUP_ROOT.iterdir()
            if path.is_dir() and path.name.startswith("daily_driver_snapshot_")
        ],
        reverse=True,
    )

    if not snapshots:
        print("\nNo Project Salus daily-driver snapshots found.")
        return 1

    latest = snapshots[0]
    manifest_path = latest / "manifest.json"

    print("\nPROJECT SALUS — LATEST SNAPSHOT")
    print("=" * 38)
    print(f"Path: {latest}")

    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        print(f"Created At: {manifest.get('created_at')}")
        print(f"Copied: {manifest.get('counts', {}).get('copied')}")
        print(f"Missing: {manifest.get('counts', {}).get('missing')}")

        if raw:
            print("\nRaw JSON:")
            print(json.dumps(manifest, indent=2))

    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Project Salus daily-driver backup command."
    )
    parser.add_argument("command", choices=["snapshot", "list", "latest"])
    parser.add_argument("--raw", action="store_true")

    args = parser.parse_args()

    if args.command == "snapshot":
        return create_snapshot(raw=args.raw)
    if args.command == "list":
        return list_snapshots(raw=args.raw)
    if args.command == "latest":
        return latest_snapshot(raw=args.raw)

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
