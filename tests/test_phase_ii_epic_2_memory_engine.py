from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from backend.services.salus_memory_service import (
    MEMORY_STORE_PATH,
    create_memory_item,
    get_memory_item,
    list_memory_items,
    memory_status,
)


client = TestClient(app)


def reset_memory_store():
    MEMORY_STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
    MEMORY_STORE_PATH.write_text("[]")


def test_phase_ii_memory_status_route():
    reset_memory_store()

    response = client.get("/api/memory/status")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["module"] == "memory_engine"


def test_phase_ii_create_and_get_memory_item():
    reset_memory_store()

    response = client.post(
        "/api/memory/item",
        json={
            "id": "memory-test-1",
            "title": "Kyle prefers direct execution blocks",
            "content": "Use copy/paste terminal blocks for Project Salus build steps.",
            "memory_type": "user",
            "domain": "project_salus",
            "source": "manual",
            "importance": 5,
            "tags": ["execution", "preference"],
        },
    )

    assert response.status_code == 200
    assert response.json()["item"]["id"] == "memory-test-1"

    get_response = client.get("/api/memory/item/memory-test-1")

    assert get_response.status_code == 200
    assert get_response.json()["item"]["memory_type"] == "user"


def test_phase_ii_memory_filters():
    reset_memory_store()

    create_memory_item(
        {
            "id": "memory-filter-1",
            "title": "Mission priority",
            "content": "Focus on high-leverage work first.",
            "memory_type": "mission",
            "domain": "execution",
            "importance": 5,
            "tags": ["mission"],
        }
    )
    create_memory_item(
        {
            "id": "memory-filter-2",
            "title": "Knowledge bridge",
            "content": "Knowledge should support judgment.",
            "memory_type": "knowledge",
            "domain": "salus",
            "importance": 4,
            "tags": ["judgment"],
        }
    )

    mission_items = list_memory_items(memory_type="mission")
    query_items = list_memory_items(query="judgment")
    tag_items = list_memory_items(tag="mission")

    assert len(mission_items) == 1
    assert mission_items[0]["id"] == "memory-filter-1"
    assert len(query_items) == 1
    assert query_items[0]["id"] == "memory-filter-2"
    assert len(tag_items) == 1
    assert tag_items[0]["id"] == "memory-filter-1"


def test_phase_ii_memory_page_loads():
    response = client.get("/command/memory")

    assert response.status_code == 200
    assert "Project Salus" in response.text
    assert "Memory Engine" in response.text


def test_phase_ii_memory_service_status():
    reset_memory_store()

    create_memory_item(
        {
            "id": "memory-status-1",
            "title": "Working memory item",
            "content": "Current mission state.",
            "memory_type": "working",
            "domain": "mission",
        }
    )

    status = memory_status()
    item = get_memory_item("memory-status-1")

    assert status["item_count"] == 1
    assert status["by_type"]["working"] == 1
    assert item is not None


def test_phase_ii_memory_docs_exist():
    assert Path("PHASE_II_EPIC_2_MEMORY_ENGINE.md").exists()
    assert Path("backend/services/salus_memory_service.py").exists()
    assert Path("backend/routes/salus_memory.py").exists()
