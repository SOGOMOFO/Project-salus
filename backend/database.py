import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "salus.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS missions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            next_action TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def seed_missions():
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM missions").fetchone()[0]

    if count == 0:
        conn.executemany("""
            INSERT INTO missions (title, status, priority, next_action)
            VALUES (?, ?, ?, ?)
        """, [
            ("Project Salus", "Active", "High", "Build Mission Control system"),
            ("Cybersecurity Training", "Active", "High", "Continue WGU/cyber path"),
            ("Echo Seven Endeavors", "Active", "Medium", "Develop business foundation")
        ])
        conn.commit()

    conn.close()
