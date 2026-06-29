import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.main import app, memory_list, memory_create, memory_search, memory_delete


class MemoryEngineTests(unittest.TestCase):
    def test_memory_engine_crud_helpers(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "salus.db"
            with patch.dict(os.environ, {"SALUS_DB_PATH": str(db_path)}, clear=False):
                from backend.memory import memory_engine as memory_module

                memory_module.initialize_memory_store()
                created = memory_module.add_memory("Project milestone", memory_type="project")
                self.assertIsNotNone(created["id"])

                memories = memory_module.list_memories()
                self.assertGreaterEqual(len(memories), 1)

                matches = memory_module.search_memories("milestone")
                self.assertGreaterEqual(len(matches), 1)

                deleted = memory_module.delete_memory(created["id"])
                self.assertTrue(deleted)
                self.assertEqual(memory_module.list_memories(), [])

    def test_memory_api_endpoints(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "salus.db"
            with patch.dict(os.environ, {"SALUS_DB_PATH": str(db_path)}, clear=False):
                from backend.memory import memory_engine as memory_module

                memory_module.initialize_memory_store()
                payload = asyncio.run(memory_create(
                    {"content": "Mission briefing", "memory_type": "mission"},
                    "salus-secure",
                ))
                self.assertEqual(payload["status"], "created")

                listed = asyncio.run(memory_list("salus-secure"))
                self.assertIn("memories", listed)

                searched = asyncio.run(memory_search("briefing", "salus-secure"))
                self.assertIn("memories", searched)

                deleted = asyncio.run(memory_delete(payload["memory"]["id"], "salus-secure"))
                self.assertEqual(deleted["status"], "deleted")


if __name__ == "__main__":
    unittest.main()
