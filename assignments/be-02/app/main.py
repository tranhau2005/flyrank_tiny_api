"""Application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.database import init_db
from app.routes.task_routes import router
from app.services.task_service import TaskNotFoundError


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="SQLite Task API", lifespan=lifespan)


@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(request: Request, exc: TaskNotFoundError):
    return JSONResponse(status_code=404, content={"error": "Task not found"})


@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=400, content={"error": "Bad request"})


app.include_router(router)


@app.get("/")
def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
def health():
    return {"status": "oke"}
