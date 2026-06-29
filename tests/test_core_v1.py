import asyncio
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.main import plugin_health, system_status
from backend.memory.service import MemoryEngine
from backend.memory.registry import discover_agents


class CoreV1Tests(unittest.TestCase):
    def test_memory_engine_persists_entries(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "memory.sqlite"
            engine = MemoryEngine(db_path=db_path)
            engine.initialize()
            engine.set("mission", {"name": "Project Salus"}, category="ops")

            reloaded = MemoryEngine(db_path=db_path)
            reloaded.initialize()
            entry = reloaded.get("mission")

            self.assertEqual(entry["key"], "mission")
            self.assertEqual(entry["value"]["name"], "Project Salus")
            self.assertEqual(entry["category"], "ops")

    def test_agent_registry_discovers_known_agents(self):
        agents = discover_agents()
        names = {agent["name"] for agent in agents}
        self.assertTrue(any("Cyber" in name for name in names))
        self.assertTrue(any("Medical" in name for name in names))

    def test_system_status_and_plugin_health_endpoints(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "memory.sqlite"
            engine = MemoryEngine(db_path=db_path)
            engine.initialize()
            with patch("backend.main.memory_engine", engine):
                payload = asyncio.run(system_status())
                plugins_payload = asyncio.run(plugin_health())

                self.assertEqual(payload["status"], "ok")
                self.assertIn("components", payload)
                self.assertIn("plugins", payload)
                self.assertIn("plugins", plugins_payload)


if __name__ == "__main__":
    unittest.main()
