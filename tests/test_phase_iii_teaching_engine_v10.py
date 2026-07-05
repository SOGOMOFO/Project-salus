from pathlib import Path

from fastapi.testclient import TestClient

from backend.core.subsystem_registry import get_subsystem, list_subsystems, route_for_intent
from backend.main import app
from backend.services.teaching_engine_service import (
    TEACHING_ENGINE_VERSION,
    TEACHING_SESSION_STORE,
    build_learning_profile,
    build_lesson,
    build_quiz,
    create_teaching_session,
    get_teaching_session,
    list_teaching_sessions,
    teaching_engine_status,
)


client = TestClient(app)


def reset_teaching_store():
    if TEACHING_SESSION_STORE.exists():
        TEACHING_SESSION_STORE.unlink()


def test_phase_iii_teaching_engine_status_route():
    reset_teaching_store()

    response = client.get("/api/teaching-engine/status")

    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "teaching_engine"
    assert data["version"] == TEACHING_ENGINE_VERSION


def test_phase_iii_teaching_profile_route():
    response = client.post(
        "/api/teaching-engine/profile",
        json={
            "user": "Kyle",
            "topic": "NIST CSF",
            "level": "intermediate",
            "goal": "Apply it to Project Salus.",
        },
    )

    assert response.status_code == 200
    profile = response.json()["profile"]
    assert profile["learner"] == "Kyle"
    assert profile["topic"] == "NIST CSF"
    assert profile["level"] == "intermediate"


def test_phase_iii_teaching_lesson_route():
    response = client.post(
        "/api/teaching-engine/lesson",
        json={"topic": "zero trust", "level": "beginner"},
    )

    assert response.status_code == 200
    lesson = response.json()["lesson"]
    assert "Zero Trust" in lesson["title"]
    assert "commander_takeaway" in lesson


def test_phase_iii_teaching_quiz_route():
    response = client.post(
        "/api/teaching-engine/quiz",
        json={"topic": "risk management"},
    )

    assert response.status_code == 200
    quiz = response.json()["quiz"]
    assert quiz["topic"] == "risk management"
    assert len(quiz["questions"]) == 3


def test_phase_iii_teaching_session_create_and_get_routes():
    reset_teaching_store()

    response = client.post(
        "/api/teaching-engine/session",
        json={
            "id": "teaching-session-test-1",
            "topic": "cloud security",
            "mode": "mission_training",
            "level": "beginner",
        },
    )

    assert response.status_code == 200
    session = response.json()["session"]
    assert session["id"] == "teaching-session-test-1"
    assert session["quiz"] is not None

    get_response = client.get("/api/teaching-engine/sessions/teaching-session-test-1")

    assert get_response.status_code == 200
    assert get_response.json()["session"]["profile"]["topic"] == "cloud security"


def test_phase_iii_teaching_sessions_list_route():
    reset_teaching_store()

    create_teaching_session(
        {
            "id": "teaching-session-list-1",
            "topic": "GRC",
            "mode": "guided_practice",
            "level": "beginner",
        }
    )

    response = client.get("/api/teaching-engine/sessions?topic=GRC")

    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_phase_iii_teaching_command_ui_loads():
    response = client.get("/command/teaching-engine")

    assert response.status_code == 200
    assert "Teaching Engine v1.0" in response.text
    assert "/api/teaching-engine/session" in response.text


def test_phase_iii_teaching_service_functions():
    reset_teaching_store()

    profile = build_learning_profile({"topic": "IAM", "level": "advanced"})
    lesson = build_lesson({"topic": "IAM", "level": "advanced"})
    quiz = build_quiz({"topic": "IAM"})
    session = create_teaching_session(
        {
            "id": "teaching-service-test-1",
            "topic": "IAM",
            "mode": "quiz",
        }
    )
    sessions = list_teaching_sessions(topic="IAM")
    loaded = get_teaching_session("teaching-service-test-1")

    assert profile["profile"]["topic"] == "IAM"
    assert lesson["lesson"]["title"].startswith("Iam")
    assert len(quiz["quiz"]["questions"]) == 3
    assert session["id"] == "teaching-service-test-1"
    assert len(sessions) == 1
    assert loaded is not None


def test_phase_iii_teaching_engine_registered_as_kernel_subsystem():
    subsystem = get_subsystem("teaching_engine")
    ids = {item["id"] for item in list_subsystems()}

    assert subsystem is not None
    assert subsystem["status_route"] == "/api/teaching-engine/status"
    assert "teaching_engine" in ids


def test_phase_iii_learning_intent_routes_to_teaching_engine():
    assert route_for_intent("learning")["subsystem_id"] == "teaching_engine"


def test_phase_iii_teaching_docs_exist():
    assert Path("SALUS_PHASE_III_TEACHING_ENGINE_V1_0.md").exists()
    assert Path("backend/services/teaching_engine_service.py").exists()
    assert Path("backend/routes/teaching_engine.py").exists()
    assert teaching_engine_status()["status"] == "ok"
