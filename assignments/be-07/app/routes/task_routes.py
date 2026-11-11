"""Task API routes."""
from fastapi import APIRouter, Response, status
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=list[TaskResponse])
def list_tasks():
    return task_service.list_task()


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int):
    return task_service.get_task(task_id)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate):
    return task_service.create_task(payload)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, payload: TaskUpdate):
    return task_service.update_task(task_id, payload)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    task_service.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
