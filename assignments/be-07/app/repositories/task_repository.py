"""Task data-access operations."""
from app.database import get_connection


def row_to_task(row):
    return None if row is None else {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


def get_all():
    with get_connection() as connection:
        return [row_to_task(row) for row in connection.execute("SELECT id, title, done FROM tasks ORDER BY id")]


def get_by_id(task_id):
    with get_connection() as connection:
        return row_to_task(connection.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)).fetchone())


def create(title, done):
    with get_connection() as connection:
        cursor = connection.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (title, int(done)))
        return row_to_task(connection.execute("SELECT id, title, done FROM tasks WHERE id = ?", (cursor.lastrowid,)).fetchone())


def update(task_id, changes):
    with get_connection() as connection:
        row = connection.execute("SELECT id, title, done FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if row is None:
            return None
        title = changes.get("title", row["title"])
        done = changes.get("done", bool(row["done"]))
        connection.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (title, int(done), task_id))
        return {"id": task_id, "title": title, "done": done}


def delete(task_id):
    with get_connection() as connection:
        return connection.execute("DELETE FROM tasks WHERE id = ?", (task_id,)).rowcount > 0
