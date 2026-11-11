"""PostgreSQL implementation of the task repository interface."""
from app.database import get_connection


def get_all():
    with get_connection() as db:
        return db.execute("SELECT id, title, done FROM tasks ORDER BY id").fetchall()


def get_by_id(task_id):
    with get_connection() as db:
        return db.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,)).fetchone()


def create(title, done):
    with get_connection() as db:
        return db.execute("INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done", (title, done)).fetchone()


def update(task_id, changes):
    with get_connection() as db:
        row = db.execute("SELECT id, title, done FROM tasks WHERE id = %s FOR UPDATE", (task_id,)).fetchone()
        if row is None:
            return None
        return db.execute("UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done", (changes.get("title", row["title"]), changes.get("done", row["done"]), task_id)).fetchone()


def delete(task_id):
    with get_connection() as db:
        return db.execute("DELETE FROM tasks WHERE id = %s", (task_id,)).rowcount > 0
