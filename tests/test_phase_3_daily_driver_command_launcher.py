import subprocess
import sys

import scripts.salus_day as salus_day


def test_salus_day_script_importable():
    assert callable(salus_day.main)
    assert callable(salus_day.run_health)
    assert callable(salus_day.run_start)
    assert callable(salus_day.run_end)
    assert callable(salus_day.run_all)


def test_salus_day_start_command_runs():
    result = subprocess.run(
        [sys.executable, "scripts/salus_day.py", "start"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "PROJECT SALUS — START MY DAY" in result.stdout
    assert "Top Actions:" in result.stdout


def test_salus_day_end_command_runs():
    result = subprocess.run(
        [sys.executable, "scripts/salus_day.py", "end"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0
    assert "PROJECT SALUS — END MY DAY AAR" in result.stdout
    assert "AAR Questions:" in result.stdout


def test_salus_day_all_command_runs():
    result = subprocess.run(
        [sys.executable, "scripts/salus_day.py", "all"],
        check=False,
        capture_output=True,
        text=True,
    )

    assert "PROJECT SALUS — DAILY DRIVER HEALTH" in result.stdout
    assert "PROJECT SALUS — START MY DAY" in result.stdout
    assert "PROJECT SALUS — END MY DAY AAR" in result.stdout
