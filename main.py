from fastapi import FastAPI,HTTPException,status, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel,field_validator
app=FastAPI()
tasks = [
    {"id": 1, "title": "Learn FastAPI", "done": False},
    {"id": 2, "title": "Build CRUD API", "done": False},
    {"id": 3, "title": "Publish to GitHub", "done": False},
]
# Schema 
class Tasks(BaseModel): 
    id: int 
    title: str
    done: bool

class TaskCreate(BaseModel): 
    title: str

class TaskUpdate(BaseModel):
    title: str | None = None
    done :bool | None = None  
    @field_validator("done",mode="before")
    @classmethod 
    def convert_empty_done_to_none(cls,value):
        if value == "": 
            return None
        return value
            
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
     
@app.put("/tasks/{id}",
         response_model=Tasks,
         summary="Update a task")
def update_task(id: int, task_data: TaskUpdate): 
    task = next((task for task in tasks if task["id"]==id), None)
    if task is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {id} was not found")
    update_data = task_data.model_dump(exclude_unset=True)
    if not update_data: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="At least one field is required")
    if "title" in update_data:
        title = update_data["title"]
        if title is None or not title.strip():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="Title is required")
        task["title"]=title.strip()
    
    if "done" in update_data: 
        
        if update_data["done"] is None: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                 detail="done is required")
        task["done"]= update_data["done"]
    return task 
@app.delete("/tasks/{id}",
            status_code=status.HTTP_204_NO_CONTENT,
            summary="Delete a task by id")
def delete_task(id: int):
    task_index = next((index for index, task in enumerate(tasks) if task["id"]==id), None)
    if task_index is None: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"Task {id} was not found")
    tasks.pop(task_index)
    return Response(
        status_code=status.HTTP_204_NO_CONTENT
    )