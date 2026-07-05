from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


def test_kernel_v09_command_ui_loads():
    response = client.get("/command/kernel")

    assert response.status_code == 200
    assert "Project Salus" in response.text
    assert "Kernel Command UI" in response.text


def test_kernel_v09_command_ui_has_orchestration_form():
    response = client.get("/command/kernel")

    assert "kernelInput" in response.text
    assert "Run Kernel Orchestration" in response.text
    assert "/api/kernel/orchestrate" in response.text


def test_kernel_v09_command_ui_displays_context_packet_panel():
    response = client.get("/command/kernel")

    assert "Context Packet" in response.text
    assert "contextPacket" in response.text


def test_kernel_v09_command_ui_displays_response_plan_panel():
    response = client.get("/command/kernel")

    assert "Response Plan" in response.text
    assert "responsePlan" in response.text


def test_kernel_v09_command_ui_displays_execution_gate_panel():
    response = client.get("/command/kernel")

    assert "Execution Gate" in response.text
    assert "executionGate" in response.text


def test_kernel_v09_command_ui_displays_doctrine_and_learning_panels():
    response = client.get("/command/kernel")

    assert "Doctrine Check" in response.text
    assert "doctrineCheck" in response.text
    assert "Learning Recommendation" in response.text
    assert "learningRecommendation" in response.text


def test_kernel_v09_docs_exist():
    assert Path("SALUS_KERNEL_V0_9.md").exists()
