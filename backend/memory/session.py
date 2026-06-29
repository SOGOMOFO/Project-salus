from __future__ import annotations

from typing import Any, Optional

from backend.database import get_connection


class SessionMemoryStore:
	def initialize(self) -> None:
		conn = get_connection()
		cur = conn.cursor()
		cur.execute(
			"""
			CREATE TABLE IF NOT EXISTS session_memories (
				id INTEGER PRIMARY KEY AUTOINCREMENT,
				session_id TEXT NOT NULL,
				key TEXT NOT NULL,
				value TEXT NOT NULL,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
				UNIQUE(session_id, key)
			)
			"""
		)
		conn.commit()
		conn.close()

	def set(self, session_id: str, key: str, value: str) -> dict[str, Any]:
		self.initialize()
		conn = get_connection()
		cur = conn.cursor()
		cur.execute(
			"""
			INSERT INTO session_memories (session_id, key, value, updated_at)
			VALUES (?, ?, ?, CURRENT_TIMESTAMP)
			ON CONFLICT(session_id, key) DO UPDATE SET
				value = excluded.value,
				updated_at = CURRENT_TIMESTAMP
			""",
			(str(session_id).strip(), str(key).strip(), str(value)),
		)
		conn.commit()
		row = cur.execute(
			"""
			SELECT id, session_id, key, value, created_at, updated_at
			FROM session_memories
			WHERE session_id = ? AND key = ?
			""",
			(str(session_id).strip(), str(key).strip()),
		).fetchone()
		conn.close()
		return {
			"id": row[0],
			"session_id": row[1],
			"key": row[2],
			"value": row[3],
			"created_at": row[4],
			"updated_at": row[5],
		}

	def list(self, session_id: str) -> list[dict[str, Any]]:
		self.initialize()
		conn = get_connection()
		cur = conn.cursor()
		rows = cur.execute(
			"""
			SELECT id, session_id, key, value, created_at, updated_at
			FROM session_memories
			WHERE session_id = ?
			ORDER BY id DESC
			""",
			(str(session_id).strip(),),
		).fetchall()
		conn.close()
		return [
			{
				"id": row[0],
				"session_id": row[1],
				"key": row[2],
				"value": row[3],
				"created_at": row[4],
				"updated_at": row[5],
			}
			for row in rows
		]

	def delete(self, session_id: str, key: Optional[str] = None) -> int:
		self.initialize()
		conn = get_connection()
		cur = conn.cursor()
		if key:
			cur.execute(
				"DELETE FROM session_memories WHERE session_id = ? AND key = ?",
				(str(session_id).strip(), str(key).strip()),
			)
		else:
			cur.execute(
				"DELETE FROM session_memories WHERE session_id = ?",
				(str(session_id).strip(),),
			)
		conn.commit()
		removed = cur.rowcount
		conn.close()
		return int(removed)
