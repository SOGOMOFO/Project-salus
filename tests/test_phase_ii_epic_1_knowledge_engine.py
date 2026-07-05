from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend.services.knowledge_service import (
    KNOWLEDGE_STORE_PATH,
    create_knowledge_item,
    get_knowledge_item,
    knowledge_status,
    list_knowledge_items,
)


client = TestClient(app)


def reset_knowledge_store():
    KNOWLEDGE_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    KNOWLEDGE_STORE_PATH.write_text("[]")


def test_phase_ii_knowledge_status_route():
    reset_knowledge_store()

    response = client.get("/api/knowledge/status")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["module"] == "knowledge_engine"


def test_phase_ii_create_and_get_knowledge_item():
    reset_knowledge_store()

    create_response = client.post(
        "/api/knowledge/item",
        json={
            "id": "knowledge-test-1",
            "title": "Judgment beats information",
            "domain": "project_salus",
            "source": "manual",
            "summary": "Project Salus should improve judgment, not just store information.",
            "content": "Information becomes valuable when converted into better decisions.",
            "confidence": "high",
            "tags": ["judgment", "doctrine"],
        },
    )

    assert create_response.status_code == 200
    item = create_response.json()["item"]
    assert item["id"] == "knowledge-test-1"

    get_response = client.get("/api/knowledge/item/knowledge-test-1")

    assert get_response.status_code == 200
    assert get_response.json()["item"]["title"] == "Judgment beats information"


def test_phase_ii_knowledge_list_filters():
    reset_knowledge_store()

    create_knowledge_item(
        {
            "id": "knowledge-filter-1",
            "title": "Cybersecurity governance",
            "domain": "cyber",
            "summary": "Governance sets decision rights.",
            "tags": ["grc", "governance"],
        }
    )
    create_knowledge_item(
        {
            "id": "knowledge-filter-2",
            "title": "Physical security risk",
            "domain": "physical_security",
            "summary": "Risk combines threat, vulnerability, and impact.",
            "tags": ["risk"],
        }
    )

    cyber_items = list_knowledge_items(domain="cyber")
    risk_items = list_knowledge_items(query="threat")
    tag_items = list_knowledge_items(tag="grc")

    assert len(cyber_items) == 1
    assert cyber_items[0]["id"] == "knowledge-filter-1"
    assert len(risk_items) == 1
    assert risk_items[0]["id"] == "knowledge-filter-2"
    assert len(tag_items) == 1
    assert tag_items[0]["id"] == "knowledge-filter-1"


def test_phase_ii_knowledge_page_loads():
    response = client.get("/command/knowledge")

    assert response.status_code == 200
    assert "Project Salus" in response.text
    assert "Knowledge Engine" in response.text


def test_phase_ii_knowledge_service_status():
    reset_knowledge_store()

    create_knowledge_item(
        {
            "id": "knowledge-status-1",
            "title": "Mission knowledge",
            "domain": "mission",
            "summary": "Mission knowledge supports better action.",
            "tags": ["mission"],
        }
    )

    status = knowledge_status()
    item = get_knowledge_item("knowledge-status-1")

    assert status["item_count"] == 1
    assert "mission" in status["domains"]
    assert item is not None
    assert item["title"] == "Mission knowledge"


def test_phase_ii_knowledge_docs_exist():
    assert Path("PHASE_II_EPIC_1_KNOWLEDGE_ENGINE.md").exists()
    assert Path("backend/services/knowledge_service.py").exists()
    assert Path("backend/routes/knowledge.py").exists()
