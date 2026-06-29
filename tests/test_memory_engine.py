import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.memory.memory_engine import (
    add_memory,
    delete_memory,
    initialize_memory_store,
    list_memories,
    search_memories,
)


class MemoryEngineTests(unittest.TestCase):
    def test_memory_engine_crud_and_search(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "salus.db"
            with patch.dict(os.environ, {"SALUS_DB_PATH": str(db_path)}, clear=False):
                initialize_memory_store()
                created = add_memory(
                    memory_type="mission",
                    title="Mission briefing",
                    content="Project Salus launch plan",
                    tags=["launch", "mission"],
                    source="unit-test",
                )
                self.assertEqual(created["memory_type"], "mission")
                self.assertEqual(created["title"], "Mission briefing")

                memories = list_memories()
                self.assertGreaterEqual(len(memories), 1)

                matches = search_memories("launch")
                self.assertGreaterEqual(len(matches), 1)

                self.assertTrue(delete_memory(created["id"]))
                self.assertEqual(list_memories(), [])

    def test_memory_engine_rejects_invalid_type(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "salus.db"
            with patch.dict(os.environ, {"SALUS_DB_PATH": str(db_path)}, clear=False):
                initialize_memory_store()
                created = add_memory(memory_type="unknown", title="Legacy note", content="Legacy content")
                self.assertEqual(created["memory_type"], "legacy")


if __name__ == "__main__":
    unittest.main()
