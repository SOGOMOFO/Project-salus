import tempfile
import unittest
from pathlib import Path

from backend.forge.generator import create_directorate
from backend.plugins.service import PluginService


class PluginsAlphaTests(unittest.TestCase):
    def test_discovery_health_toggle_and_manifest_validation(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            created = create_directorate("Plugin Alpha", project_root=root)
            slug = created["slug"]

            service = PluginService(project_root=root)
            plugins = service.discover()
            self.assertTrue(any(item["slug"] == slug for item in plugins))

            health = service.health()
            self.assertIn("status", health)
            self.assertGreaterEqual(health["count"], 1)

            validated = service.validate_manifest(slug)
            self.assertTrue(validated["valid"])

            off = service.disable(slug)
            self.assertFalse(off["enabled"])
            on = service.enable(slug)
            self.assertTrue(on["enabled"])


if __name__ == "__main__":
    unittest.main()
