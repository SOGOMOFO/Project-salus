import json
import sqlite3
from pathlib import Path
from typing import Any, Optional


class MemoryEngine:
    def __init__(self, db_path: Optional[Path | str] = None):
        self.db_path = Path(db_path or Path(__file__).resolve().parent / "memory.sqlite")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS memory_entries (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    category TEXT NOT NULL DEFAULT 'general',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def set(self, key: str, value: Any, category: str = "general") -> None:
        payload = json.dumps(value)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO memory_entries (key, value, category, updated_at)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    category = excluded.category,
                    updated_at = CURRENT_TIMESTAMP
                """,
                (key, payload, category),
            )
            conn.commit()

    def get(self, key: str) -> Optional[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT key, value, category, created_at, updated_at FROM memory_entries WHERE key = ?",
                (key,),
            ).fetchone()
        if row is None:
            return None
        return {
            "key": row[0],
            "value": json.loads(row[1]),
            "category": row[2],
            "created_at": row[3],
            "updated_at": row[4],
        }

    def list(self, category: Optional[str] = None) -> list[dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            if category:
                rows = conn.execute(
                    "SELECT key, value, category, created_at, updated_at FROM memory_entries WHERE category = ? ORDER BY key",
                    (category,),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT key, value, category, created_at, updated_at FROM memory_entries ORDER BY key"
                ).fetchall()

        return [
            {
                "key": row[0],
                "value": json.loads(row[1]),
                "category": row[2],
                "created_at": row[3],
                "updated_at": row[4],
            }
            for row in rows
        ]
