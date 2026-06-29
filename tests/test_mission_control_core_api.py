import asyncio
import unittest
from unittest.mock import patch

from backend.main import app
from backend.memory.service import MemoryEngine
from backend.main import core_status, core_memory_status, core_agents, core_plugins_status


class MissionControlCoreApiTests(unittest.TestCase):
    def test_core_status_endpoint_payload(self):
        payload = asyncio.run(core_status())
        self.assertEqual(payload["status"], "ok")
        self.assertIn("components", payload)

    def test_core_memory_status_endpoint_payload(self):
        payload = asyncio.run(core_memory_status())
        self.assertEqual(payload["status"], "ok")
        self.assertIn("memory", payload)

    def test_core_agents_endpoint_payload(self):
        payload = asyncio.run(core_agents("salus-secure"))
        self.assertIn("agents", payload)
        self.assertGreaterEqual(len(payload["agents"]), 1)

    def test_core_plugins_status_endpoint_payload(self):
        payload = asyncio.run(core_plugins_status("salus-secure"))
        self.assertIn("plugins", payload)
        self.assertGreaterEqual(len(payload["plugins"]), 1)


if __name__ == "__main__":
    unittest.main()
