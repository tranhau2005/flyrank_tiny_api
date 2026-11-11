"""SQLite persistence for the task API."""
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

DATABASE_PATH = Path(os.getenv("TASK_DATABASE_PATH", Path(__file__).resolve().parent.parent / "tasks.db"))


@contextmanager
def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def init_db():
    with get_connection() as connection:
        exists = connection.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='tasks'"
        ).fetchone()
        connection.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0 CHECK (done IN (0, 1))
        )""")
        if not exists:
            connection.executemany("INSERT INTO tasks (title, done) VALUES (?, ?)", [
                ("Learn SQLite", 0), ("Build CRUD API", 0), ("Test persistence", 0),
            ])
