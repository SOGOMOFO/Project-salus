from pathlib import Path


def test_packaging_files_exist():
    required = [
        ".env.example",
        "Dockerfile",
        "docker-compose.yml",
        "Makefile",
        "scripts/startup_check.py",
        "scripts/smoke_check.sh",
        "run_praevale.sh",
    ]

    for path in required:
        assert Path(path).exists(), f"Missing {path}"


def test_env_example_has_required_keys():
    text = Path(".env.example").read_text()

    required = [
        "SALUS_ENV=",
        "SALUS_PORT=",
        "SALUS_AUTH_ENABLED=",
        "SALUS_LOCAL_PASSWORD=",
        "SALUS_LOCAL_TOKEN=",
        "SALUS_ALLOW_EXTERNAL_ACTIONS=",
        "SALUS_ALLOW_MODEL_PROVIDER_EXTERNAL_CALLS=",
        "SALUS_ALLOW_CONNECTOR_WRITES=",
    ]

    for key in required:
        assert key in text


def test_dockerfile_points_to_backend_main():
    text = Path("Dockerfile").read_text()

    assert "backend.main:app" in text
    assert "8010" in text


def test_makefile_has_core_commands():
    text = Path("Makefile").read_text()

    for command in ["test:", "run:", "smoke:", "docker-build:", "docker-up:", "docker-down:"]:
        assert command in text


def test_startup_check_mentions_required_routes():
    text = Path("scripts/startup_check.py").read_text()

    required_routes = [
        "/mission-control/v1",
        "/mission-control/login",
        "/api/mission-control/dashboard",
        "/api/mission-control/mvp-readiness",
        "/api/mission-control/auth/status",
    ]

    for route in required_routes:
        assert route in text
