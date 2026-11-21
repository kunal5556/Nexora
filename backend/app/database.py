import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

from app.config import settings

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata TEXT,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages (session_id, id);

CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    system_prompt TEXT,
    created_at TEXT NOT NULL
);
"""

INSERT_MESSAGE_SQL = (
    "INSERT INTO messages (session_id, role, content, metadata, created_at) VALUES (?, ?, ?, ?, ?)"
)


@contextmanager
def open_connection():
    connection = sqlite3.connect(settings.database_path, timeout=10)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    finally:
        connection.close()


def init_db():
    folder = os.path.dirname(settings.database_path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open_connection() as connection:
        connection.executescript(SCHEMA_SQL)


def is_database_reachable():
    try:
        with open_connection() as connection:
            connection.execute("SELECT 1")
        return True
    except sqlite3.Error:
        return False


def current_timestamp():
    return datetime.now(timezone.utc).isoformat()


def get_session_messages(session_id):
    with open_connection() as connection:
        return connection.execute(
            "SELECT role, content, metadata FROM messages WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()


def get_session_system_prompt(session_id):
    with open_connection() as connection:
        row = connection.execute(
            "SELECT system_prompt FROM sessions WHERE session_id = ?",
            (session_id,),
        ).fetchone()
    return row["system_prompt"] if row else None


def save_chat_exchange(session_id, user_message, assistant_reply, metadata, system_prompt):
    created_at = current_timestamp()
    with open_connection() as connection:
        connection.execute(
            "INSERT OR IGNORE INTO sessions (session_id, system_prompt, created_at) VALUES (?, NULL, ?)",
            (session_id, created_at),
        )
        if system_prompt:
            connection.execute(
                "UPDATE sessions SET system_prompt = ? WHERE session_id = ?",
                (system_prompt, session_id),
            )
        connection.execute(INSERT_MESSAGE_SQL, (session_id, "user", user_message, None, created_at))
        connection.execute(INSERT_MESSAGE_SQL, (session_id, "assistant", assistant_reply, json.dumps(metadata), created_at))
