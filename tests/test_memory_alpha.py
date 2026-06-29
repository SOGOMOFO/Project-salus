import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from backend.memory.importance import calculate_importance
from backend.memory.memory_engine import add_memory, initialize_memory_store, list_memories
from backend.memory.search import semantic_search_memories
from backend.memory.session import SessionMemoryStore


class MemoryAlphaTests(unittest.TestCase):
    def test_importance_scoring_bounds(self):
        low = calculate_importance(content="short")
        high = calculate_importance(
            content="critical mission note " * 80,
            tags=["mission", "important", "critical"],
            source="unit-test",
        )
        self.assertGreaterEqual(low, 0.0)
        self.assertLessEqual(high, 1.0)
        self.assertGreater(high, low)

    def test_session_memory_crud(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "salus.db"
            with patch.dict(os.environ, {"SALUS_DB_PATH": str(db_path)}, clear=False):
                store = SessionMemoryStore()
                created = store.set("session-a", "goal", "Ship alpha sprint")
                self.assertEqual(created["session_id"], "session-a")

                rows = store.list("session-a")
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]["key"], "goal")

                removed = store.delete("session-a", "goal")
                self.assertEqual(removed, 1)

    def test_semantic_search_interface(self):
        memories = [
            {"id": 1, "title": "Mission Brief", "content": "Investor alpha sprint execution", "tags": ["mission"]},
            {"id": 2, "title": "Weather", "content": "Cloudy day", "tags": []},
        ]
        matches = semantic_search_memories("investor sprint", memories, limit=5)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["id"], 1)
        self.assertIn("semantic_score", matches[0])

    def test_persistent_memory_includes_importance(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "salus.db"
            with patch.dict(os.environ, {"SALUS_DB_PATH": str(db_path)}, clear=False):
                initialize_memory_store()
                created = add_memory(
                    memory_type="mission",
                    title="Alpha",
                    content="Critical alpha sprint checkpoint",
                    tags=["critical", "mission"],
                )
                self.assertIn("importance", created)
                rows = list_memories("mission")
                self.assertGreaterEqual(rows[0]["importance"], 0.0)


if __name__ == "__main__":
    unittest.main()
