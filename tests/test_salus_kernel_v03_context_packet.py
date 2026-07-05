from pathlib import Path

from fastapi.testclient import TestClient

from backend.core.context_packet import (
    CONTEXT_PACKET_VERSION,
    build_context_packet,
    context_packet_status,
)
from backend.core.kernel import route_request
from backend.main import app


client = TestClient(app)


def test_kernel_v03_context_status_route():
    response = client.get("/api/kernel/context/status")

    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "context_packet"
    assert data["version"] == CONTEXT_PACKET_VERSION


def test_kernel_v03_context_packet_route():
    response = client.post(
        "/api/kernel/context",
        json={"user": "Kyle", "input": "Help me decide what to build next."},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["module"] == "context_packet"
    assert data["classification"]["intent"] == "judgment"
    assert data["selected_subsystem"]["subsystem_id"] == "judgment"
    assert "identity" in data
    assert "memory" in data
    assert "knowledge" in data
    assert "judgment" in data


def test_kernel_v03_context_packet_requires_input():
    response = client.post("/api/kernel/context", json={"user": "Kyle"})

    assert response.status_code == 400


def test_kernel_v03_route_request_includes_context_packet():
    result = route_request({"user": "Kyle", "input": "Remember this mission context."})

    assert "context_packet" in result
    assert result["context_packet"]["classification"]["intent"] == "memory"
    assert result["context_packet"]["selected_subsystem"]["subsystem_id"] == "memory"


def test_kernel_v03_context_packet_service():
    packet = build_context_packet({"input": "Help me study cybersecurity."})
    status = context_packet_status()

    assert packet["classification"]["intent"] == "learning"
    assert packet["selected_subsystem"]["subsystem_id"] == "teaching_engine"
    assert status["status"] == "ok"


def test_kernel_v03_operating_rules_present():
    packet = build_context_packet({"input": "Should I pursue this opportunity?"})

    assert any("accountability" in rule.lower() for rule in packet["operating_rules"])
    assert any("evidence" in rule.lower() for rule in packet["operating_rules"])


def test_kernel_v03_docs_exist():
    assert Path("SALUS_KERNEL_V0_3.md").exists()
    assert Path("backend/core/context_packet.py").exists()
