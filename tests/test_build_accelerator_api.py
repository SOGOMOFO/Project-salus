from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_build_accelerator_framework_loads():
    response = client.get("/build-accelerator/framework")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "Project Salus Build Accelerator & System Map V1"
    assert data["core_modules_tracked"] >= 10
    assert "system_map" in data["outputs"]


def test_system_map_reports_modules():
    response = client.get("/build-accelerator/system-map")
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "build_accelerator_system_map"
    assert data["total_modules"] >= 10
    assert "modules" in data
    assert data["completion_score"] <= 100


def test_next_build_recommends_with_focus():
    response = client.post("/build-accelerator/next-build", json={"focus": "console", "capacity": 2})
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "build_accelerator_next_build"
    assert len(data["top_recommendations"]) == 2
    assert data["top_recommendations"][0]["build_score"] <= 100
    assert data["top_recommendations"][0]["recommended_scope"]


def test_build_sprint_returns_tasks_and_checklist():
    response = client.post(
        "/build-accelerator/sprint",
        json={
            "sprint_name": "Fast Build Sprint",
            "focus": "client",
            "capacity": 2,
            "include_release_checklist": True,
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "build_accelerator_sprint"
    assert len(data["tasks"]) == 2
    assert "release_checklist" in data
    assert data["next_action"]


def test_release_checklist_returns_commands():
    response = client.post(
        "/build-accelerator/release-checklist",
        json={"changed_files": ["backend/main.py"]},
    )
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "build_accelerator_release_checklist"
    assert "pytest -q" in data["commands"]
    assert data["stop_conditions"]


def test_smoke_test_plan_includes_framework_endpoints():
    response = client.post("/build-accelerator/smoke-test-plan", json={"include_optional": True})
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "build_accelerator_smoke_test_plan"
    assert "/build-accelerator/framework" in data["endpoints"]
    assert "/command-center/framework" in data["endpoints"]


def test_commit_pack_builds_git_commands():
    response = client.post(
        "/build-accelerator/commit-pack",
        json={
            "files": [
                "backend/main.py",
                "backend/routes/build_accelerator.py",
            ],
            "message": "add build accelerator system map v1",
        },
    )
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "build_accelerator_commit_pack"
    assert 'git commit -m "add build accelerator system map v1"' in data["commands"]
