
from fastapi.testclient import TestClient

import backend.main as main_module
from backend.main import app


client = TestClient(app)


RESET_PAYLOAD = {"confirmation": "RESET_PROJECT_SALUS_DEV_DATA"}


def test_sprint_12_schoolhouse_course_persists_to_json():
    client.post("/api/dev/reset", json=RESET_PAYLOAD)

    response = client.post(
        "/api/schoolhouse/course",
        json={
            "name": "D333 Ethics in Technology",
            "code": "D333",
            "school": "WGU",
            "priority": "high",
            "current_task": "Task 1 ethical technology use scenario",
            "next_action": "Draft AI-driven hiring system section",
        },
    )

    assert response.status_code == 200

    saved = main_module._sprint01_load_json(main_module._SPRINT12_SCHOOLHOUSE_COURSES_FILE, [])

    assert len(saved) == 1
    assert saved[0]["name"] == "D333 Ethics in Technology"

    main_module._schoolhouse_courses.clear()
    main_module._schoolhouse_courses.extend(
        main_module._sprint01_load_json(main_module._SPRINT12_SCHOOLHOUSE_COURSES_FILE, [])
    )

    assert len(main_module._schoolhouse_courses) == 1
    assert main_module._schoolhouse_courses[0]["code"] == "D333"


def test_sprint_12_schoolhouse_study_session_persists_to_json():
    client.post("/api/dev/reset", json=RESET_PAYLOAD)

    response = client.post(
        "/api/schoolhouse/study-session",
        json={
            "course": "Practical Applications of Prompt",
            "objective": "Practice OA prompt constraints.",
            "duration_minutes": 45,
            "material": "OA review",
            "notes": "One-question-at-a-time quiz drill.",
            "confidence_before": 4,
            "confidence_after": 6,
            "blockers": ["Needs repetition"],
            "next_action": "Run wrong-answer review",
        },
    )

    assert response.status_code == 200

    saved = main_module._sprint01_load_json(main_module._SPRINT12_SCHOOLHOUSE_STUDY_SESSIONS_FILE, [])

    assert len(saved) == 1
    assert saved[0]["course"] == "Practical Applications of Prompt"
    assert saved[0]["readiness_signal"] == "improved"


def test_sprint_12_charisma_assessment_and_aar_persist_to_json():
    client.post("/api/dev/reset", json=RESET_PAYLOAD)

    assessment_response = client.post(
        "/api/skills/charisma/self-assessment",
        json={
            "context": "Cybersecurity interview",
            "presence": 7,
            "clarity": 7,
            "listening": 6,
            "emotional_control": 8,
            "confidence": 7,
            "empathy": 6,
            "framing": 6,
            "trust_building": 6,
            "ethical_alignment": 10,
        },
    )

    assert assessment_response.status_code == 200

    aar_response = client.post(
        "/api/skills/charisma/conversation-aar",
        json={
            "objective": "Explain Project Salus clearly.",
            "audience": "Potential advisor",
            "what_i_said": "I explained the dashboard and modules.",
            "how_they_responded": "They understood and asked for use cases.",
            "did_i_listen_well": "Yes",
            "did_i_stay_calm": "Yes",
            "did_i_build_trust": "Somewhat",
            "scorecard": {
                "presence": 7,
                "clarity": 7,
                "listening": 6,
                "emotional_control": 8,
                "confidence": 7,
                "empathy": 6,
                "framing": 6,
                "trust_building": 6,
                "ethical_alignment": 10,
            },
        },
    )

    assert aar_response.status_code == 200

    saved_assessments = main_module._sprint01_load_json(main_module._SPRINT12_CHARISMA_SELF_ASSESSMENTS_FILE, [])
    saved_aars = main_module._sprint01_load_json(main_module._SPRINT12_CHARISMA_CONVERSATION_AARS_FILE, [])

    assert len(saved_assessments) == 1
    assert saved_assessments[0]["context"] == "Cybersecurity interview"
    assert len(saved_aars) == 1
    assert saved_aars[0]["objective"] == "Explain Project Salus clearly."


def test_sprint_12_dev_reset_clears_persistent_capability_data():
    client.post("/api/dev/reset", json=RESET_PAYLOAD)

    client.post(
        "/api/schoolhouse/course",
        json={"name": "Reset Test Course", "code": "RESET", "school": "WGU"},
    )

    client.post(
        "/api/skills/charisma/self-assessment",
        json={
            "context": "Reset test",
            "presence": 5,
            "clarity": 5,
            "listening": 5,
            "emotional_control": 5,
            "confidence": 5,
            "empathy": 5,
            "framing": 5,
            "trust_building": 5,
            "ethical_alignment": 10,
        },
    )

    reset_response = client.post("/api/dev/reset", json=RESET_PAYLOAD)

    assert reset_response.status_code == 200

    assert main_module._schoolhouse_courses == []
    assert main_module._charisma_self_assessments == []

    assert main_module._sprint01_load_json(main_module._SPRINT12_SCHOOLHOUSE_COURSES_FILE, []) == []
    assert main_module._sprint01_load_json(main_module._SPRINT12_CHARISMA_SELF_ASSESSMENTS_FILE, []) == []
