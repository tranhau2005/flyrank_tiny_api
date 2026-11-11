# BE-04: Containerized PostgreSQL task API

This is the BE-02 API with its repository swapped from SQLite to PostgreSQL. The service, routes and schemas are unchanged. Compose starts PostgreSQL with a named volume and waits for the database health check before starting the API. `init.sql` runs once when the database volume is first created.

Create a local `.env` file containing `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, and `DATABASE_URL`. For Compose, use host `db` in the URL: `postgresql://USER:PASSWORD@db:5432/DATABASE`. Use a URL-safe local password and keep all values consistent. Then run:

```sh
docker compose up --build
```

The API is at `http://localhost:8000/docs`. To verify persistence, create a task with `POST /tasks`, run `docker compose restart`, then retrieve the same task. `docker compose down` retains the volume; `docker compose down -v` deletes it. Never commit `.env`. No dotenv example is committed because the workspace rules prohibit committing dotenv files; the variables are documented above.

Validation: the PostgreSQL repository passed create, update, read, delete and missing-ID checks against an isolated local PostgreSQL 18 instance. A created row survived stopping and restarting that database. Docker was unavailable, so the Compose startup and container restart test have not yet been run.
