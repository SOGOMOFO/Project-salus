import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Optional

SUPPORTED_MEMORY_TYPES = {"user", "project", "agent", "mission", "legacy"}


def get_db_path() -> Path:
    configured = os.getenv("SALUS_DB_PATH")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parent.parent.parent / "salus.db"


def get_connection() -> sqlite3.Connection:
    db_path = get_db_path()
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_memory_store() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            memory_type TEXT NOT NULL,
            metadata TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()


def _normalize_memory_type(memory_type: Optional[str]) -> str:
    if memory_type in SUPPORTED_MEMORY_TYPES:
        return memory_type
    return "legacy"


def _serialize_metadata(metadata: Optional[dict[str, Any]]) -> str:
    if not metadata:
        return "{}"
    return json.dumps(metadata)


def _deserialize_metadata(payload: Optional[str]) -> dict[str, Any]:
    if not payload:
        return {}
    try:
        return json.loads(payload)
    except (TypeError, json.JSONDecodeError):
        return {}


def add_memory(content: str, memory_type: str = "legacy", metadata: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    if not content or not str(content).strip():
        raise ValueError("content is required")

    normalized_type = _normalize_memory_type(memory_type)
    payload = metadata or {}
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO memories (content, memory_type, metadata, created_at, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """,
        (str(content).strip(), normalized_type, _serialize_metadata(payload)),
    )
    conn.commit()
    memory_id = cur.lastrowid
    conn.close()
    return {
        "id": memory_id,
        "content": str(content).strip(),
        "memory_type": normalized_type,
        "metadata": payload,
    }


def list_memories(memory_type: Optional[str] = None) -> list[dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    if memory_type:
        cur.execute(
            "SELECT id, content, memory_type, metadata, created_at, updated_at FROM memories WHERE memory_type = ? ORDER BY id DESC",
            (_normalize_memory_type(memory_type),),
        )
    else:
        cur.execute("SELECT id, content, memory_type, metadata, created_at, updated_at FROM memories ORDER BY id DESC")

    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "content": row[1],
            "memory_type": row[2],
            "metadata": row[3] and eval(row[3], {}, {}),
            "created_at": row[4],
            "updated_at": row[5],
        }
        for row in rows
    ]


def search_memories(query: str, memory_type: Optional[str] = None) -> list[dict[str, Any]]:
    if not query or not str(query).strip():
        return []

    conn = get_connection()
    cur = conn.cursor()
    search_term = f"%{str(query).strip()}%"
    if memory_type:
        cur.execute(
            "SELECT id, content, memory_type, metadata, created_at, updated_at FROM memories WHERE memory_type = ? AND content LIKE ? ORDER BY id DESC",
            (_normalize_memory_type(memory_type), search_term),
        )
    else:
        cur.execute(
            "SELECT id, content, memory_type, metadata, created_at, updated_at FROM memories WHERE content LIKE ? ORDER BY id DESC",
            (search_term,),
        )

    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "content": row[1],
            "memory_type": row[2],
            "metadata": row[3] and eval(row[3], {}, {}),
            "created_at": row[4],
            "updated_at": row[5],
        }
        for row in rows
    ]


def delete_memory(memory_id: int) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM memories WHERE id = ?", (int(memory_id),))
    conn.commit()
    deleted = cur.rowcount > 0
    conn.close()
    return deleted
