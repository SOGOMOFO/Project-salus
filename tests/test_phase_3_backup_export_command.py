import subprocess
import sys

import scripts.salus_backup as salus_backup


def test_backup_script_importable():
    assert callable(salus_backup.main)
    assert callable(salus_backup.create_snapshot)
    assert callable(salus_backup.list_snapshots)
    assert callable(salus_backup.latest_snapshot)


def test_backup_list_command_runs():
    result = subprocess.run(
        [sys.executable, "scripts/salus_backup.py", "list"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "PROJECT SALUS — BACKUP SNAPSHOTS" in result.stdout


def test_backup_snapshot_command_runs():
    result = subprocess.run(
        [sys.executable, "scripts/salus_backup.py", "snapshot"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "PROJECT SALUS — DAILY DRIVER SNAPSHOT" in result.stdout
    assert "Copied:" in result.stdout


def test_backup_latest_command_runs_after_snapshot():
    subprocess.run(
        [sys.executable, "scripts/salus_backup.py", "snapshot"],
        check=False,
        capture_output=True,
        text=True,
    )

    result = subprocess.run(
        [sys.executable, "scripts/salus_backup.py", "latest"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "PROJECT SALUS — LATEST SNAPSHOT" in result.stdout
