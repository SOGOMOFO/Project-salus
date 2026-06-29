import tempfile
import unittest
import asyncio
from pathlib import Path
from unittest.mock import patch

from backend.core.agent_runtime import AgentRuntime
from backend.core.mission_planner import MissionPlanner
from backend.main import (
    core_status,
    core_agents,
    run_core_agent,
    core_missions,
    create_core_mission,
    complete_core_mission,
)
from backend.memory.memory_engine import initialize_memory_store, list_memories


class DummyRequest:
    def __init__(self, payload):
        self._payload = payload

    async def json(self):
        return self._payload


class SalusCoreV2Tests(unittest.TestCase):
    def test_agent_runtime_register_run_and_memory_write(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "salus_v2.db"
            with patch.dict("os.environ", {"SALUS_DB_PATH": str(db_path)}, clear=False):
                initialize_memory_store()
                runtime = AgentRuntime()

                def handler(payload: dict[str, str]):
                    return f"processed: {payload.get('objective', '')}", 0.95

                runtime.register_agent(
                    name="Test Agent",
                    mission="Validate runtime behavior",
                    handler=handler,
                )
                result = runtime.run_agent("Test Agent", {"objective": "verify"}, important=True)

                self.assertEqual(result["status"], "ok")
                self.assertEqual(result["agent"], "Test Agent")
                self.assertIn("input", result)
                self.assertIn("output", result)
                self.assertIn("confidence", result)
                self.assertIn("timestamp", result)

                memories = list_memories(memory_type="agent")
                self.assertGreaterEqual(len(memories), 1)

    def test_mission_planner_create_list_complete(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "salus_v2.db"
            with patch.dict("os.environ", {"SALUS_DB_PATH": str(db_path)}, clear=False):
                planner = MissionPlanner()
                first = planner.create_mission(title="Low Priority", priority="low")
                second = planner.create_mission(title="High Priority", priority="high")

                missions = planner.list_missions()
                self.assertGreaterEqual(len(missions), 2)
                self.assertEqual(missions[0]["priority"], "high")
                self.assertEqual(missions[0]["title"], "High Priority")

                completed = planner.complete_mission(second["id"])
                self.assertIsNotNone(completed)
                self.assertEqual(completed["status"], "completed")
                self.assertIsNotNone(completed["completed_at"])

                self.assertNotEqual(first["id"], second["id"])

    def test_commander_api_core_v2_endpoints(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "salus_v2.db"
            with patch.dict("os.environ", {"SALUS_DB_PATH": str(db_path)}, clear=False):
                status_payload = asyncio.run(core_status())
                self.assertEqual(status_payload["status"], "ok")

                agents_payload = asyncio.run(core_agents("salus-secure"))
                agents = agents_payload["agents"]
                self.assertGreaterEqual(len(agents), 1)

                agent_name = agents[0]["name"]
                run_payload = asyncio.run(
                    run_core_agent(
                        agent_name,
                        DummyRequest({"input": {"objective": "api check"}, "important": True}),
                        "salus-secure",
                    )
                )
                self.assertEqual(run_payload["status"], "ok")
                self.assertEqual(run_payload["agent"], agent_name)

                create_payload = asyncio.run(
                    create_core_mission(
                        DummyRequest(
                            {
                                "title": "API mission",
                                "description": "validate commander endpoints",
                                "priority": "high",
                            }
                        ),
                        "salus-secure",
                    )
                )
                self.assertEqual(create_payload["status"], "created")
                mission_id = create_payload["mission"]["id"]

                list_payload = asyncio.run(core_missions("salus-secure"))
                self.assertGreaterEqual(len(list_payload["missions"]), 1)

                complete_payload = asyncio.run(complete_core_mission(mission_id, "salus-secure"))
                self.assertEqual(complete_payload["status"], "completed")


if __name__ == "__main__":
    unittest.main()
