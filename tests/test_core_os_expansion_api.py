from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def reset_core_os():
    response = client.post(
        "/api/core-os/reset",
        json={"confirmation": "RESET_CORE_OS_DEV_DATA"},
    )
    assert response.status_code == 200


def test_core_os_reset_requires_confirmation():
    response = client.post("/api/core-os/reset", json={"confirmation": "wrong"})
    assert response.status_code == 400


def test_health_status_and_checkin():
    reset_core_os()

    status_response = client.get("/health/status")
    assert status_response.status_code == 200
    assert status_response.json()["records"]["checkins"] == 0

    checkin_response = client.post(
        "/health/check-in",
        json={
            "sleep_quality": "medium",
            "energy": "medium",
            "training": "walk",
            "nutrition": "simple meal prep",
            "hydration": "good",
            "next_action": "Do 30 minutes of zone 2 cardio.",
        },
    )

    assert checkin_response.status_code == 200
    assert checkin_response.json()["health_checkin"]["next_action"] == "Do 30 minutes of zone 2 cardio."

    updated_status = client.get("/health/status").json()
    assert updated_status["records"]["checkins"] == 1


def test_health_brief():
    reset_core_os()

    response = client.get("/health/brief")
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "health_brief"
    assert "next_action" in data


def test_business_status_and_mission():
    reset_core_os()

    status_response = client.get("/business/status")
    assert status_response.status_code == 200
    assert status_response.json()["records"]["missions"] == 0

    mission_response = client.post(
        "/business/mission",
        json={
            "title": "AI Governance Readiness Offer",
            "intent": "Create a small federal-facing assessment offer.",
            "domain": "Echo Seven",
            "priority": "high",
            "status": "planned",
            "risk": "medium",
            "next_action": "Draft one-page offer.",
        },
    )

    assert mission_response.status_code == 200
    assert mission_response.json()["business_mission"]["title"] == "AI Governance Readiness Offer"

    updated_status = client.get("/business/status").json()
    assert updated_status["records"]["missions"] == 1
    assert updated_status["records"]["active_missions"] == 1


def test_business_brief():
    reset_core_os()

    response = client.get("/business/brief")
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "business_brief"
    assert "next_action" in data


def test_legacy_status_and_brief():
    status_response = client.get("/legacy/status")
    assert status_response.status_code == 200
    assert status_response.json()["module"] == "legacy"

    brief_response = client.get("/legacy/brief")
    assert brief_response.status_code == 200
    assert "great-grandchildren" in brief_response.json()["question"]


def test_command_readiness_risks_and_next_actions():
    reset_core_os()

    readiness_response = client.get("/api/core-os/command/readiness")
    assert readiness_response.status_code == 200
    readiness = readiness_response.json()
    assert readiness["module"] == "command_readiness"
    assert readiness["readiness_level"] in ["green", "amber", "red"]

    risks_response = client.get("/api/core-os/command/risks")
    assert risks_response.status_code == 200
    risks = risks_response.json()
    assert risks["module"] == "command_risks"
    assert risks["count"] >= 1

    actions_response = client.get("/api/core-os/command/next-actions")
    assert actions_response.status_code == 200
    actions = actions_response.json()
    assert actions["module"] == "command_next_actions"
    assert len(actions["actions"]) >= 3


def test_command_brief():
    reset_core_os()

    response = client.get("/api/core-os/command/brief")
    assert response.status_code == 200

    data = response.json()
    assert data["module"] == "command_brief"
    assert data["title"] == "Project Salus Command Brief"
    assert "readiness" in data
    assert "risks" in data
    assert "next_actions" in data
