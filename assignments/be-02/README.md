# BE-02: SQLite task API

This assignment moves the original task CRUD API into SQLite while keeping the same task endpoints. SQLite needs no separate server and is suitable for a small local exercise. On first startup it creates `tasks.db` beside this README and seeds three examples; an existing (even empty) table is never seeded again. Set `TASK_DATABASE_PATH` to use another database file.

```sh
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8000
```

Open `http://localhost:8000/docs` for the API. `GET /tasks`, `GET /tasks/{id}`, `POST /tasks`, `PUT /tasks/{id}`, and `DELETE /tasks/{id}` use SQL. Invalid bodies return 400 and unknown tasks 404. Example SQL: `SELECT * FROM tasks WHERE done = 1;`.

Run `python -m unittest -v test_api` to exercise CRUD, invalid input, missing IDs, database reinitialization, and a direct SQL update. The tests use an isolated temporary database; they do not start a network server. The [database screenshot](screenshots/database.jpg) shows the real seeded table queried by a temporary read-only SQLite viewer.

Separately, a local Uvicorn process was started against a temporary SQLite file, a task was created over HTTP, and the process was stopped and restarted. The same task was then retrieved over HTTP from the restarted process.
