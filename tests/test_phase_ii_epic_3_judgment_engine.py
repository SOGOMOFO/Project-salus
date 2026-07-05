from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend.services.judgment_engine_service import (
    JUDGMENT_STORE_PATH,
    create_judgment_item,
    get_judgment_item,
    judgment_status,
    list_judgment_items,
    score_judgment,
)


client = TestClient(app)


def reset_judgment_store():
    JUDGMENT_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    JUDGMENT_STORE_PATH.write_text("[]")


def test_phase_ii_judgment_status_route():
    reset_judgment_store()

    response = client.get("/api/judgment-engine/status")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["module"] == "judgment_engine"


def test_phase_ii_judgment_score_route():
    response = client.post(
        "/api/judgment-engine/score",
        json={
            "evidence": ["tests pass", "clear next action"],
            "risks": ["local persistence only"],
            "options": ["build", "pause"],
            "confidence": "high",
            "recommendation": "pursue",
            "next_action": "Implement local scoring.",
        },
    )

    assert response.status_code == 200
    score = response.json()["score"]
    assert score["score"] >= 60
    assert score["readiness"] in {"moderate", "strong"}


def test_phase_ii_create_and_get_judgment_item():
    reset_judgment_store()

    response = client.post(
        "/api/judgment-engine/item",
        json={
            "id": "judgment-test-1",
            "decision": "Build Judgment Engine",
            "context": "Project Salus needs decision-quality tracking.",
            "options": ["build now", "pause"],
            "evidence": ["Phase II roadmap exists", "Memory and Knowledge engines exist"],
            "risks": ["local persistence only"],
            "confidence": "high",
            "recommendation": "pursue",
            "next_action": "Create service, routes, tests, and docs.",
        },
    )

    assert response.status_code == 200
    item = response.json()["item"]
    assert item["id"] == "judgment-test-1"
    assert item["judgment_score"]["score"] >= 60

    get_response = client.get("/api/judgment-engine/item/judgment-test-1")

    assert get_response.status_code == 200
    assert get_response.json()["item"]["decision"] == "Build Judgment Engine"


def test_phase_ii_judgment_filters():
    reset_judgment_store()

    create_judgment_item(
        {
            "id": "judgment-filter-1",
            "decision": "Launch feature",
            "context": "Feature has strong evidence.",
            "evidence": ["tests pass"],
            "risks": ["minor polish"],
            "recommendation": "pursue",
            "next_action": "Launch beta.",
        }
    )
    create_judgment_item(
        {
            "id": "judgment-filter-2",
            "decision": "Delay feature",
            "context": "Risk is too high.",
            "evidence": ["missing tests"],
            "risks": ["breakage"],
            "recommendation": "pause",
            "next_action": "Add tests.",
        }
    )

    pursue_items = list_judgment_items(recommendation="pursue")
    query_items = list_judgment_items(query="delay")

    assert len(pursue_items) == 1
    assert pursue_items[0]["id"] == "judgment-filter-1"
    assert len(query_items) == 1
    assert query_items[0]["id"] == "judgment-filter-2"


def test_phase_ii_judgment_page_loads():
    response = client.get("/command/judgment")

    assert response.status_code == 200
    assert "Project Salus" in response.text
    assert "Judgment Engine" in response.text


def test_phase_ii_judgment_service_status():
    reset_judgment_store()

    create_judgment_item(
        {
            "id": "judgment-status-1",
            "decision": "Use local scoring first",
            "context": "Avoid external dependency early.",
            "evidence": ["stable tests"],
            "risks": ["limited sophistication"],
            "recommendation": "pursue",
        }
    )

    status = judgment_status()
    item = get_judgment_item("judgment-status-1")

    assert status["item_count"] == 1
    assert status["by_recommendation"]["pursue"] == 1
    assert item is not None


def test_phase_ii_judgment_docs_exist():
    assert Path("PHASE_II_EPIC_3_JUDGMENT_ENGINE.md").exists()
    assert Path("backend/services/judgment_engine_service.py").exists()
    assert Path("backend/routes/judgment_engine.py").exists()
