from fastapi import FastAPI,HTTPException,status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
app=FastAPI()
tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build CRUD API", "done": False},
    {"id": 3, "title": "Publish to GitHub", "done": False},
]
class Tasks(BaseModel): 
    id: int 
    title: str
    done: bool

@app.get("/")
def main():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}
@app.get("/health")
def healthcheck():
    return {"status":"oke"}

@app.get("/tasks",
         response_model=list[Tasks],
         summary="Response all tasks")
def get_tasks():
    """Return all tasks in memory"""
    return tasks
@app.get("/tasks/{id}",
         response_model=Tasks,
         summary="Return the task by ID")
def get_task(id: int): 
    task= next((task for task in tasks if task["id"]==id), None)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Task {id} was not found")
    return task

class TaskCreate(BaseModel): 
    title: str
@app.post("/tasks",
          response_model=Tasks,
          status_code=status.HTTP_201_CREATED,
          summary="Create new task")
def create_task(task_data:TaskCreate):
    if task_data.title is None or not task_data.title.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Title is required")
    next_id = max((task["id"] for task in tasks), default=0)+1 
    new_task={
        "id": next_id,
        "title": task_data.title.strip(),
        "done": False
    } 
    tasks.append(new_task)
    return new_task
     