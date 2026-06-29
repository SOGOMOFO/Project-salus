import tempfile
import unittest
from pathlib import Path

from backend.forge import sdk


class ForgeSdkTests(unittest.TestCase):
    def test_create_directorate_cli_creates_boilerplate(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            result = sdk.main([
                "create-directorate",
                "Legacy Intelligence",
                "--project-root",
                str(project_root),
            ])

            self.assertEqual(result, 0)
            expected_files = [
                project_root / "backend" / "api" / "legacy_intelligence.py",
                project_root / "backend" / "services" / "legacy_intelligence_service.py",
                project_root / "backend" / "agents" / "legacy_intelligence_agent.py",
                project_root / "backend" / "directorates" / "legacy_intelligence.py",
                project_root / "docs" / "legacy_intelligence.md",
                project_root / "tests" / "test_legacy_intelligence.py",
            ]
            for path in expected_files:
                self.assertTrue(path.exists(), f"missing {path}")
                self.assertTrue(path.read_text(encoding="utf-8"))

            registry_path = project_root / "backend" / "directorates" / "registry.py"
            registry_text = registry_path.read_text(encoding="utf-8")
            self.assertIn("LegacyIntelligenceDirectorate", registry_text)

    def test_create_directorate_rejects_duplicates(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            first_result = sdk.main([
                "create-directorate",
                "Legacy Intelligence",
                "--project-root",
                str(project_root),
            ])
            second_result = sdk.main([
                "create-directorate",
                "Legacy Intelligence",
                "--project-root",
                str(project_root),
            ])

            self.assertEqual(first_result, 0)
            self.assertNotEqual(second_result, 0)


if __name__ == "__main__":
    unittest.main()
