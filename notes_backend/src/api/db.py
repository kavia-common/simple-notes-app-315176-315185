"""
SQLite database access utilities for the Notes API.

The database container exposes a shared SQLite DB file path. We connect to it
directly from the backend using the SQLITE_DB environment variable.

If SQLITE_DB is not set, we fall back to a local `notes.db` in this container
to keep development friction low.
"""

from __future__ import annotations

import os
import sqlite3
from typing import Optional

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    updated_at TEXT NOT NULL DEFAULT (CURRENT_TIMESTAMP)
);

CREATE TRIGGER IF NOT EXISTS notes_updated_at
AFTER UPDATE ON notes
FOR EACH ROW
BEGIN
    UPDATE notes
    SET updated_at = CURRENT_TIMESTAMP
    WHERE id = OLD.id;
END;
"""


# PUBLIC_INTERFACE
def get_db_path() -> str:
    """Return the SQLite DB file path used by the backend."""
    return os.getenv("SQLITE_DB", os.path.join(os.getcwd(), "notes.db"))


# PUBLIC_INTERFACE
def get_connection() -> sqlite3.Connection:
    """Create and return a SQLite connection (row_factory enabled)."""
    conn = sqlite3.connect(get_db_path(), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# PUBLIC_INTERFACE
def init_db(conn: Optional[sqlite3.Connection] = None) -> None:
    """Ensure the database schema exists (idempotent)."""
    close_after = False
    if conn is None:
        conn = get_connection()
        close_after = True

    try:
        # Execute each statement separately for compatibility with SQLite.
        cur = conn.cursor()
        for stmt in [s.strip() for s in SCHEMA_SQL.split(";") if s.strip()]:
            cur.execute(stmt)
        conn.commit()
    finally:
        if close_after:
            conn.close()
