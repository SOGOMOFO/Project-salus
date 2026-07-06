from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_mission_control_create_mission_form_redirects():
    response = client.post(
        "/mission-control/mission",
        data={
            "title": "Browser Mission Test",
            "priority": "high",
            "status": "active",
            "next_action": "Verify browser form creation",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/ui"


def test_mission_control_create_sitrep_form_redirects():
    response = client.post(
        "/mission-control/sitrep",
        data={
            "top_priority": "Build browser workflow",
            "blocker": "None",
            "action_1": "Test form",
            "action_2": "Commit form",
            "action_3": "Use dashboard",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/ui"


def test_mission_control_create_aar_form_redirects():
    response = client.post(
        "/mission-control/aar",
        data={
            "what_happened": "Added browser forms.",
            "what_worked": "Dynamic table insert avoided schema mismatch.",
            "what_failed": "",
            "lesson": "Move fast by using existing architecture.",
            "next_action": "Add status buttons.",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/mission-control/ui"
