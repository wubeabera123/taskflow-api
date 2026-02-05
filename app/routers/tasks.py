from fastapi import APIRouter, HTTPException
from app.schemas.task import Task, TaskCreate

router = APIRouter()

# Fake in-memory "database"
tasks = []
task_id_counter = 1

# Create Task
@router.post("/tasks", response_model=Task)
def create_task(task: TaskCreate):
    global task_id_counter
    new_task = Task(id=task_id_counter, **task.dict())
    tasks.append(new_task)
    task_id_counter += 1
    return new_task

# Get All Tasks
@router.get("/tasks", response_model=list[Task])
def get_tasks():
    return tasks

# Get Task by ID
@router.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

# Delete Task by ID
@router.delete("/tasks/{task_id}", response_model=dict)
def delete_task(task_id: int):
    global tasks
    for task in tasks:
        if task.id == task_id:
            tasks = [t for t in tasks if t.id != task_id]
            return {"message": "Task deleted"}
    raise HTTPException(status_code=404, detail="Task not found")
