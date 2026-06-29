import json
import os
import sqlite3
from pathlib import Path
from typing import Any, Optional

from backend.database import get_connection as get_db_connection
from backend.memory.models import SUPPORTED_MEMORY_TYPES


def get_db_path() -> Path:
    configured = os.getenv("SALUS_DB_PATH")
    if configured:
        return Path(configured)
    return Path(__file__).resolve().parent.parent.parent / "salus.db"


def get_connection() -> sqlite3.Connection:
    return get_db_connection()


def initialize_memory_store() -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            memory_type TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            tags TEXT,
            source TEXT,
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


def _serialize_tags(tags: Optional[list[str]]) -> str:
    if not tags:
        return "[]"
    return json.dumps(tags)


def _deserialize_tags(payload: Optional[str]) -> list[str]:
    if not payload:
        return []
    try:
        loaded = json.loads(payload)
        return loaded if isinstance(loaded, list) else []
    except (TypeError, json.JSONDecodeError):
        return []


def add_memory(
    content: Optional[str] = None,
    memory_type: str = "legacy",
    title: str = "",
    tags: Optional[list[str]] = None,
    source: Optional[str] = None,
    **kwargs: Any,
) -> dict[str, Any]:
    if content is None and "content" in kwargs:
        content = kwargs.pop("content")
    if title == "" and "title" in kwargs:
        title = kwargs.pop("title")
    if tags is None and "tags" in kwargs:
        tags = kwargs.pop("tags")
    if source is None and "source" in kwargs:
        source = kwargs.pop("source")

    if not content or not str(content).strip():
        raise ValueError("content is required")

    normalized_type = _normalize_memory_type(memory_type)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO memories (memory_type, title, content, tags, source, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """,
        (
            normalized_type,
            str(title or "").strip(),
            str(content).strip(),
            _serialize_tags(tags),
            str(source or "").strip() or None,
        ),
    )
    conn.commit()
    memory_id = cur.lastrowid
    row = cur.execute(
        "SELECT id, memory_type, title, content, tags, source, created_at, updated_at FROM memories WHERE id = ?",
        (memory_id,),
    ).fetchone()
    conn.close()
    return {
        "id": row[0],
        "memory_type": row[1],
        "title": row[2],
        "content": row[3],
        "tags": _deserialize_tags(row[4]),
        "source": row[5],
        "created_at": row[6],
        "updated_at": row[7],
    }


def list_memories(memory_type: Optional[str] = None) -> list[dict[str, Any]]:
    conn = get_connection()
    cur = conn.cursor()
    if memory_type:
        cur.execute(
            "SELECT id, memory_type, title, content, tags, source, created_at, updated_at FROM memories WHERE memory_type = ? ORDER BY id DESC",
            (_normalize_memory_type(memory_type),),
        )
    else:
        cur.execute(
            "SELECT id, memory_type, title, content, tags, source, created_at, updated_at FROM memories ORDER BY id DESC"
        )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "memory_type": row[1],
            "title": row[2],
            "content": row[3],
            "tags": _deserialize_tags(row[4]),
            "source": row[5],
            "created_at": row[6],
            "updated_at": row[7],
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
            "SELECT id, memory_type, title, content, tags, source, created_at, updated_at FROM memories WHERE memory_type = ? AND (title LIKE ? OR content LIKE ? OR source LIKE ?) ORDER BY id DESC",
            (_normalize_memory_type(memory_type), search_term, search_term, search_term),
        )
    else:
        cur.execute(
            "SELECT id, memory_type, title, content, tags, source, created_at, updated_at FROM memories WHERE title LIKE ? OR content LIKE ? OR source LIKE ? ORDER BY id DESC",
            (search_term, search_term, search_term),
        )
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": row[0],
            "memory_type": row[1],
            "title": row[2],
            "content": row[3],
            "tags": _deserialize_tags(row[4]),
            "source": row[5],
            "created_at": row[6],
            "updated_at": row[7],
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
