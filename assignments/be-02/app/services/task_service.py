"""Task business logic."""
from app.repositories import task_repository


class TaskNotFoundError(Exception):
    pass


def list_task():
    return task_repository.get_all()


def get_task(task_id):
    task = task_repository.get_by_id(task_id)
    if task is None:
        raise TaskNotFoundError
    return task


def create_task(payload):
    return task_repository.create(payload.title, False)


def update_task(task_id, payload):
    task = task_repository.update(task_id, payload.model_dump(exclude_unset=True))
    if task is None:
        raise TaskNotFoundError
    return task


def delete_task(task_id):
    if not task_repository.delete(task_id):
        raise TaskNotFoundError
