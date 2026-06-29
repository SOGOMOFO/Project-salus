import asyncio
import unittest
from unittest.mock import patch

from backend.main import app
from backend.memory.service import MemoryEngine
from backend.main import core_status, core_memory_status, core_agents, core_plugins_status, mission_control_status


class MissionControlCoreApiTests(unittest.TestCase):
    @staticmethod
    def _collect_paths(routes):
        paths = set()
        for route in routes:
            if hasattr(route, "path"):
                paths.add(route.path)
            if hasattr(route, "routes"):
                nested = getattr(route, "routes")
                if isinstance(nested, list):
                    paths.update(MissionControlCoreApiTests._collect_paths(nested))
        return paths

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

    def test_mission_control_status_alias(self):
        payload = asyncio.run(mission_control_status())
        self.assertEqual(payload["status"], "ok")

    def test_required_route_prefixes_are_registered(self):
        paths = set(app.openapi().get("paths", {}).keys())
        required = {
            "/status",
            "/core",
            "/memory",
            "/missions",
            "/plugins",
            "/forge",
            "/security/status",
            "/security/audit",
            "/investor-intelligence/status",
        }
        for item in required:
            self.assertIn(item, paths)


if __name__ == "__main__":
    unittest.main()
