"""Inngest example: enqueue a report and poll its status."""
import datetime
import logging
import uuid
import inngest
import inngest.fast_api
from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI(title="Background report jobs")
client = inngest.Inngest(app_id="report-api", logger=logging.getLogger("uvicorn"))
reports = {}

@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Invalid request"})

class ReportRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=200)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/reports", status_code=202)
async def create_report(payload: ReportRequest):
    topic = payload.topic.strip()
    if not topic:
        raise HTTPException(400, "Topic is required")
    report_id = str(uuid.uuid4())
    reports[report_id] = {"id": report_id, "topic": topic, "status": "pending"}
    try:
        await client.send(inngest.Event(id=report_id, name="report/requested", data={"id": report_id, "topic": topic}))
    except Exception as exc:
        del reports[report_id]
        raise HTTPException(503, "Job service unavailable") from exc
    return {"id": report_id, "status": "pending"}

@app.get("/reports/{report_id}")
def get_report(report_id: str):
    if report_id not in reports:
        raise HTTPException(404, "Report not found")
    return reports[report_id]

@client.create_function(fn_id="say-hello", trigger=inngest.TriggerEvent(event="test/hello"))
async def say_hello(ctx: inngest.Context):
    await ctx.step.sleep("wait", datetime.timedelta(seconds=5))
    return "Hello from the background!"

@client.create_function(fn_id="make-report", retries=2, trigger=inngest.TriggerEvent(event="report/requested"))
async def make_report(ctx: inngest.Context):
    data = ctx.event.data
    await ctx.step.sleep("do-the-slow-work", datetime.timedelta(seconds=8))
    def build():
        report_id, topic = str(data["id"]), str(data["topic"])
        if topic == "fail":
            if ctx.attempt >= 2 and report_id in reports:
                reports[report_id]["status"] = "failed"
            raise RuntimeError("The report oven is broken!")
        if report_id not in reports:
            raise RuntimeError("Report state missing after process restart")
        reports[report_id].update(status="done", result=f"Report about {topic}")
        return reports[report_id]
    return await ctx.step.run("build-report", build)

@client.create_function(fn_id="heartbeat", trigger=inngest.TriggerCron(cron="* * * * *"))
async def heartbeat(ctx: inngest.Context):
    counts = {state: sum(r["status"] == state for r in reports.values()) for state in ("pending", "done", "failed")}
    ctx.logger.info("Reports: %s", counts)
    return counts

ingest_functions = [say_hello, make_report, heartbeat]
inngest.fast_api.serve(app, client, ingest_functions)
