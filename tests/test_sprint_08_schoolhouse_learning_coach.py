
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_sprint_08_schoolhouse_status():
    response = client.get("/api/schoolhouse/status")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["module"] == "schoolhouse_learning_coach"
    assert "quiz_mode" in data["capabilities"]


def test_sprint_08_schoolhouse_course_create_and_list():
    create_response = client.post(
        "/api/schoolhouse/course",
        json={
            "name": "Practical Applications of Prompt",
            "code": "DXXX",
            "school": "WGU",
            "priority": "high",
            "competencies": ["Prompt engineering", "Prompt evaluation"],
            "current_task": "OA retake preparation",
            "next_action": "Run one-question quiz drills",
        },
    )

    assert create_response.status_code == 200
    created = create_response.json()["course"]
    assert created["name"] == "Practical Applications of Prompt"

    list_response = client.get("/api/schoolhouse/courses")

    assert list_response.status_code == 200
    data = list_response.json()
    assert data["status"] == "ok"
    assert data["count"] >= 1


def test_sprint_08_schoolhouse_study_session_and_daily_brief():
    session_response = client.post(
        "/api/schoolhouse/study-session",
        json={
            "course": "D333",
            "objective": "Understand ethical technology use scenario structure.",
            "duration_minutes": 45,
            "material": "AI-driven hiring system scenario",
            "notes": "Need to compare deontology and utilitarianism.",
            "confidence_before": 4,
            "confidence_after": 6,
            "blockers": ["Rubric wording"],
            "next_action": "Draft Task 1 outline",
        },
    )

    assert session_response.status_code == 200
    session = session_response.json()["study_session"]
    assert session["readiness_signal"] == "improved"

    brief_response = client.get("/api/schoolhouse/daily-brief")

    assert brief_response.status_code == 200
    brief = brief_response.json()["brief"]
    assert "recommended_focus" in brief
    assert brief["recommended_study_block_minutes"] == 45


def test_sprint_08_schoolhouse_quiz_mode():
    response = client.post(
        "/api/schoolhouse/quiz",
        json={
            "course": "Prompt Engineering",
            "topic": "Prompt constraints",
            "difficulty": "medium",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["mode"] == "one_question_at_a_time"
    assert "question" in data


def test_sprint_08_schoolhouse_wrong_answer_review():
    response = client.post(
        "/api/schoolhouse/wrong-answer-review",
        json={
            "course": "Prompt Engineering",
            "question": "What improves prompt specificity?",
            "selected_answer": "Longer prompts always",
            "correct_answer": "Clear constraints and context",
            "why_wrong": "Length alone does not improve specificity.",
            "rule_to_remember": "Specificity comes from relevant context, constraints, and success criteria.",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert "teaching_point" in data
    assert data["review"]["rule_to_remember"]


def test_sprint_08_schoolhouse_writing_task():
    response = client.post(
        "/api/schoolhouse/writing-task",
        json={
            "course": "D333",
            "task_name": "Ethical Technology Use Scenarios",
            "prompt": "Analyze ethical issues in an AI-driven hiring system.",
            "rubric_items": [
                "Identify ethical issue",
                "Apply professional code",
                "Compare ethical frameworks",
            ],
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert len(data["section_plan"]) == 3
    assert data["rule"].startswith("Answer the rubric directly")
