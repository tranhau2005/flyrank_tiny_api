# BE-06: Your first background job

FastAPI accepts a report request, sends `report/requested` to Inngest, and returns 202; the worker sleeps durably, performs a step, and updates an in-memory report. `GET /reports/{id}` polls status; `/health` checks the API. `say-hello` is triggered by `test/hello`; `heartbeat` runs every minute. The `fail` topic deliberately fails with two retries. Input errors should not be retried; transient worker failures may be retried.

```sh
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
INNGEST_DEV=1 uvicorn main:app --port 8000
# In another terminal:
npx inngest-cli@latest dev --host 127.0.0.1 --no-discovery -u http://127.0.0.1:8000/api/inngest
```

The Inngest dashboard is `http://localhost:8288`. Daily 08:00 UTC is `0 8 * * *`; Sunday 22:00 UTC is `0 22 * * 0`. This teaching example keeps report state in memory: restarting the API loses it even if Inngest remembers the run. A production service needs persistent state and a transactional outbox for reliable event delivery.

A local run returned `202 {"status":"pending"}` in 0.03 seconds and later `done` with a report. A run with topic `fail` retried twice (three attempts total) and ended `failed`; the heartbeat ran twice one minute apart and `say-hello` completed. See [the local dashboard](screenshots/inngest-runs.jpg).
