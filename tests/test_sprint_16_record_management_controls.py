
from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


RESET_PAYLOAD = {"confirmation": "RESET_PROJECT_SALUS_DEV_DATA"}


def test_sprint_16_record_management_state_endpoint():
    response = client.get("/api/command/records")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "ok"
    assert data["module"] == "record_management_controls"
    assert "schoolhouse_courses" in data["groups"]
    assert "charisma_self_assessments" in data["groups"]
    assert "delete" in data["actions"]
    assert "archive" in data["actions"]


def test_sprint_16_record_management_page_loads():
    response = client.get("/command/records")

    assert response.status_code == 200
    assert "Record Management" in response.text
    assert "Archive Record" in response.text
    assert "Delete Record" in response.text
    assert "DELETE_PROJECT_SALUS_RECORD" in response.text


def test_sprint_16_archive_schoolhouse_course():
    client.post("/api/dev/reset", json=RESET_PAYLOAD)

    create_response = client.post(
        "/api/schoolhouse/course",
        json={
            "id": "sprint16-course-1",
            "name": "Sprint 16 Archive Test",
            "code": "S16",
            "school": "WGU",
        },
    )

    assert create_response.status_code == 200

    archive_response = client.post(
        "/api/command/records/archive",
        json={
            "group": "schoolhouse_courses",
            "id": "sprint16-course-1",
        },
    )

    assert archive_response.status_code == 200
    data = archive_response.json()

    assert data["status"] == "ok"
    assert data["action"] == "archive"
    assert data["record"]["archived"] is True


def test_sprint_16_delete_charisma_assessment_requires_confirmation():
    client.post("/api/dev/reset", json=RESET_PAYLOAD)

    create_response = client.post(
        "/api/skills/charisma/self-assessment",
        json={
            "id": "sprint16-charisma-1",
            "context": "Sprint 16 delete test",
            "presence": 7,
            "clarity": 7,
            "listening": 7,
            "emotional_control": 7,
            "confidence": 7,
            "empathy": 7,
            "framing": 7,
            "trust_building": 7,
            "ethical_alignment": 10,
        },
    )

    assert create_response.status_code == 200

    bad_delete = client.post(
        "/api/command/records/delete",
        json={
            "group": "charisma_self_assessments",
            "id": "sprint16-charisma-1",
            "confirmation": "wrong",
        },
    )

    assert bad_delete.status_code == 400

    good_delete = client.post(
        "/api/command/records/delete",
        json={
            "group": "charisma_self_assessments",
            "id": "sprint16-charisma-1",
            "confirmation": "DELETE_PROJECT_SALUS_RECORD",
        },
    )

    assert good_delete.status_code == 200
    assert good_delete.json()["status"] == "ok"

    records = client.get("/api/command/records").json()
    assert records["counts"]["charisma_self_assessments"] == 0
