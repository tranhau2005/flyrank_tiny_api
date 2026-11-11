"""Exercise the ASGI API and persistence against a real SQLite file."""
import asyncio
import json
import os
import sqlite3
import tempfile
import unittest


class TaskApiTest(unittest.TestCase):
    def test_crud_validation_and_restart(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.environ["TASK_DATABASE_PATH"] = os.path.join(tmp, "tasks.db")
            from app.main import app
            from app.database import init_db
            init_db()

            async def request(method, path, body=None):
                content = json.dumps(body).encode() if body is not None else b""
                received = False
                async def receive():
                    nonlocal received
                    if not received:
                        received = True
                        return {"type": "http.request", "body": content, "more_body": False}
                    return {"type": "http.disconnect"}
                messages = []
                async def send(message):
                    messages.append(message)
                scope = {"type": "http", "asgi": {"version": "3.0"}, "http_version": "1.1", "method": method, "scheme": "http", "path": path, "raw_path": path.encode(), "query_string": b"", "headers": [(b"content-type", b"application/json")], "client": ("test", 1), "server": ("test", 80), "root_path": ""}
                await app(scope, receive, send)
                status = next(m["status"] for m in messages if m["type"] == "http.response.start")
                data = b"".join(m.get("body", b"") for m in messages if m["type"] == "http.response.body")
                return status, json.loads(data) if data else None

            def call(*args):
                return asyncio.run(request(*args))

            self.assertEqual(len(call("GET", "/tasks")[1]), 3)
            self.assertEqual(call("POST", "/tasks", {})[0], 400)
            self.assertEqual(call("PUT", "/tasks/1", {"done": None})[0], 400)
            self.assertEqual(call("GET", "/tasks/999")[0], 404)
            status, task = call("POST", "/tasks", {"title": "  persist me  "})
            self.assertEqual((status, task["title"]), (201, "persist me"))
            task_id = task["id"]
            self.assertTrue(call("PUT", f"/tasks/{task_id}", {"done": True})[1]["done"])
            init_db()
            self.assertTrue(call("GET", f"/tasks/{task_id}")[1]["done"])
            with sqlite3.connect(os.environ["TASK_DATABASE_PATH"]) as db:
                db.execute("UPDATE tasks SET title = ? WHERE id = ?", ("changed in SQL", task_id))
            self.assertEqual(call("GET", f"/tasks/{task_id}")[1]["title"], "changed in SQL")
            self.assertEqual(call("DELETE", f"/tasks/{task_id}")[0], 204)
            self.assertEqual(call("DELETE", f"/tasks/{task_id}")[0], 404)
            for task in call("GET", "/tasks")[1]:
                call("DELETE", f"/tasks/{task['id']}")
            init_db()
            self.assertEqual(call("GET", "/tasks")[1], [])


if __name__ == "__main__":
    unittest.main()
