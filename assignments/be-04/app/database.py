"""PostgreSQL connections for the task repository."""
import os
from contextlib import contextmanager
import psycopg
from psycopg.rows import dict_row


@contextmanager
def get_connection():
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("Set DATABASE_URL before starting the application")
    with psycopg.connect(url, row_factory=dict_row) as connection:
        yield connection


def init_db():
    # Schema initialization is performed by PostgreSQL's Docker entrypoint.
    with get_connection() as connection:
        connection.execute("SELECT 1 FROM tasks LIMIT 1")
