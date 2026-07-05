from pathlib import Path

from fastapi.testclient import TestClient

from backend.core.kernel import kernel_status
from backend.core.learning_capture import (
    LEARNING_CAPTURE_VERSION,
    LEARNING_STORE_PATH,
    capture_learning,
    get_learning_record,
    learning_capture_status,
    list_learning_records,
)
from backend.main import app


client = TestClient(app)


def reset_learning_store():
    if LEARNING_STORE_PATH.exists():
        LEARNING_STORE_PATH.unlink()


def test_kernel_v06_learning_capture_status_route():
    reset_learning_store()

    response = client.get("/api/kernel/learning-capture/status")

    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "learning_capture"
    assert data["version"] == LEARNING_CAPTURE_VERSION


def test_kernel_v06_capture_learning_route():
    reset_learning_store()

    response = client.post(
        "/api/kernel/learning-capture",
        json={
            "id": "lesson-test-1",
            "input": "Kernel context packet caused circular import.",
            "outcome": "partial",
            "lesson": "Peer modules should not import each other circularly.",
            "future_rule": "Put shared classification logic in independent modules.",
            "confidence": "high",
            "tags": ["kernel", "architecture"],
        },
    )

    assert response.status_code == 200
    record = response.json()["record"]
    assert record["id"] == "lesson-test-1"
    assert record["outcome"] == "partial"


def test_kernel_v06_list_and_get_learning_records():
    reset_learning_store()

    capture_learning(
        {
            "id": "lesson-filter-1",
            "input": "Tests failed during import.",
            "outcome": "failed",
            "lesson": "Import boundaries matter.",
            "future_rule": "Move shared logic to dependency-free core modules.",
            "tags": ["imports"],
        }
    )
    capture_learning(
        {
            "id": "lesson-filter-2",
            "input": "Tests passed after fix.",
            "outcome": "success",
            "lesson": "Independent classifier resolved import issue.",
            "future_rule": "Check import graph before adding kernel dependencies.",
            "tags": ["kernel"],
        }
    )

    failed = list_learning_records(outcome="failed")
    query = list_learning_records(query="classifier")
    tagged = list_learning_records(tag="imports")
    record = get_learning_record("lesson-filter-2")

    assert len(failed) == 1
    assert failed[0]["id"] == "lesson-filter-1"
    assert len(query) == 1
    assert query[0]["id"] == "lesson-filter-2"
    assert len(tagged) == 1
    assert tagged[0]["id"] == "lesson-filter-1"
    assert record is not None


def test_kernel_v06_learning_records_route():
    reset_learning_store()

    capture_learning(
        {
            "id": "lesson-route-1",
            "input": "Save checkpoint.",
            "outcome": "success",
            "lesson": "Checkpoint makes continuation safer.",
            "future_rule": "Create checkpoints after passing tests.",
        }
    )

    response = client.get("/api/kernel/learning-capture/records")

    assert response.status_code == 200
    assert response.json()["count"] == 1


def test_kernel_v06_learning_record_get_route():
    reset_learning_store()

    capture_learning(
        {
            "id": "lesson-route-get-1",
            "input": "Fix a failing import.",
            "outcome": "success",
            "lesson": "Small targeted fixes beat broad changes.",
            "future_rule": "Fix root cause before touching tests.",
        }
    )

    response = client.get("/api/kernel/learning-capture/records/lesson-route-get-1")

    assert response.status_code == 200
    assert response.json()["record"]["id"] == "lesson-route-get-1"


def test_kernel_v06_kernel_status_includes_learning_capture():
    status = kernel_status()

    assert "learning_capture" in status
    assert status["learning_capture"]["module"] == "learning_capture"


def test_kernel_v06_docs_exist():
    assert Path("SALUS_KERNEL_V0_6.md").exists()
    assert Path("backend/core/learning_capture.py").exists()
    assert learning_capture_status()["status"] == "ok"
