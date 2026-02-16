from fastapi import APIRouter, HTTPException
from app.schemas.task import TaskCreate
from app.services.prisma import db

router = APIRouter()


# CREATE TASK
@router.post("/tasks")
async def create_task(task: TaskCreate):
    new_task = await db.task.create(
        data={
            "title": task.title,
            "description": task.description,
            "userId": 1   # temporary until auth phase
        }
    )
    return new_task


# GET ALL
@router.get("/tasks")
async def get_tasks():
    return await db.task.find_many()


# GET ONE
@router.get("/tasks/{task_id}")
async def get_task(task_id: int):
    task = await db.task.find_unique(where={"id": task_id})

    if not task:
        raise HTTPException(404, "Task not found")

    return task


# DELETE
@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    try:
        await db.task.delete(where={"id": task_id})
        return {"message": "Task deleted"}
    except:
        raise HTTPException(404, "Task not found")
