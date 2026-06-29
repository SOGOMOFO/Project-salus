import tempfile
import unittest
from pathlib import Path

from backend.forge import sdk


class ForgeSdkTests(unittest.TestCase):
    def test_create_directorate_cli_creates_v4_boilerplate(self):
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
                project_root / "backend" / "directorates" / "legacy_intelligence" / "__init__.py",
                project_root / "backend" / "directorates" / "legacy_intelligence" / "agent.py",
                project_root / "backend" / "directorates" / "legacy_intelligence" / "service.py",
                project_root / "backend" / "directorates" / "legacy_intelligence" / "api.py",
                project_root / "backend" / "directorates" / "legacy_intelligence" / "models.py",
                project_root / "backend" / "directorates" / "legacy_intelligence" / "memory.py",
                project_root / "backend" / "directorates" / "legacy_intelligence" / "prompts.py",
                project_root / "backend" / "directorates" / "legacy_intelligence" / "manifest.json",
                project_root / "docs" / "legacy_intelligence" / "README.md",
                project_root / "tests" / "legacy_intelligence" / "test_legacy_intelligence.py",
                project_root / "frontend" / "navigation.json",
                project_root / "docs" / "index.md",
            ]
            for path in expected_files:
                self.assertTrue(path.exists(), f"missing {path}")
                self.assertTrue(path.read_text(encoding="utf-8"))

            registry_path = project_root / "backend" / "directorates" / "registry.py"
            registry_text = registry_path.read_text(encoding="utf-8")
            self.assertIn("LegacyIntelligenceDirectorate", registry_text)
            self.assertIn("legacy_intelligence", (project_root / "backend" / "api" / "routes.py").read_text(encoding="utf-8"))
            self.assertIn("Legacy Intelligence", (project_root / "frontend" / "navigation.json").read_text(encoding="utf-8"))
            self.assertIn("Legacy Intelligence", (project_root / "docs" / "index.md").read_text(encoding="utf-8"))

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

    def test_validate_and_rollback_work(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self.assertEqual(sdk.main([
                "create-directorate",
                "Medical Intelligence",
                "--project-root",
                str(project_root),
            ]), 0)
            self.assertEqual(sdk.main([
                "validate",
                "--project-root",
                str(project_root),
            ]), 0)
            self.assertEqual(sdk.main([
                "rollback",
                "Medical Intelligence",
                "--project-root",
                str(project_root),
            ]), 0)
            self.assertFalse((project_root / "backend" / "directorates" / "medical_intelligence").exists())

    def test_plugins_cli_discovers_and_toggles(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self.assertEqual(sdk.main([
                "create-directorate",
                "Plugin Demo",
                "--project-root",
                str(project_root),
            ]), 0)
            self.assertEqual(sdk.main([
                "plugins",
                "--project-root",
                str(project_root),
            ]), 0)
            self.assertTrue((project_root / "backend" / "directorates" / "plugin_demo" / "plugin.json").exists())
            self.assertEqual(sdk.main([
                "enable",
                "plugin_demo",
                "--project-root",
                str(project_root),
            ]), 0)
            self.assertEqual(sdk.main([
                "disable",
                "plugin_demo",
                "--project-root",
                str(project_root),
            ]), 0)

    def test_generator_alias_commands(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            self.assertEqual(sdk.main([
                "create-directorate",
                "Alpha Intel",
                "--project-root",
                str(project_root),
            ]), 0)

            for command in [
                "generate-agent",
                "generate-service",
                "generate-api",
                "generate-tests",
                "generate-docs",
                "update-registry",
            ]:
                self.assertEqual(sdk.main([
                    command,
                    "Alpha Intel",
                    "--project-root",
                    str(project_root),
                ]), 0)


if __name__ == "__main__":
    unittest.main()
