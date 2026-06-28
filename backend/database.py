import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "salus.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS missions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        status TEXT NOT NULL,
        priority TEXT NOT NULL,
        next_action TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS sitreps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        top_priority TEXT,
        blocker TEXT,
        action_1 TEXT,
        action_2 TEXT,
        action_3 TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS agents (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT NOT NULL,
        mission TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def seed_data():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM missions")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO missions (title,status,priority,next_action) VALUES (?,?,?,?)",
            [
                ("Project Salus", "Active", "High", "Build Mission Control system"),
                ("Cybersecurity Training", "Active", "High", "Continue WGU cyber path"),
                ("Echo Seven Endeavors", "Active", "Medium", "Develop business foundation"),
            ]
        )

    cur.execute("SELECT COUNT(*) FROM agents")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO agents (name,status,mission) VALUES (?,?,?)",
            [
                ("Commander Agent", "Standby", "Prioritize missions"),
                ("Research Agent", "Standby", "Support analysis"),
                ("Cyber Agent", "Standby", "Track cyber training"),
                ("Health Agent", "Standby", "Track health intelligence"),
                ("Finance Agent", "Standby", "Track finance intelligence"),
            ]
        )

    conn.commit()
    conn.close()
