from fastapi import APIRouter, HTTPException
from app.schemas.task import TaskCreate
from app.services.prisma import db
from fastapi import Depends
from app.core.dependencies import get_current_user, require_role
from fastapi import HTTPException


router = APIRouter(prefix="/tasks", tags=["Tasks"])


# CREATE TASK
@router.post("/")
async def create_task(
    task: TaskCreate,
    current_user=Depends(get_current_user)
):
    return await db.task.create(
        data={
            "title": task.title,
            "description": task.description,
            "userId": current_user.id
        }
    )

# GET ALL


@router.get("/")
async def get_tasks(
    skip: int = 0,
    limit: int = 10,
    current_user=Depends(get_current_user)
):
    total = await db.task.count(
        where={"userId": current_user.id}
    )

    tasks = await db.task.find_many(
        where={"userId": current_user.id},
        skip=skip,
        take=limit,
        order={"createdAt": "desc"}
    )

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": tasks
    }

# GET ONE


@router.get("/tasks/{task_id}")
async def get_task(task_id: int):
    task = await db.task.find_unique(where={"id": task_id})

    if not task:
        raise HTTPException(404, "Task not found")

    return task


@router.put("/{task_id}")
async def update_task(
    task_id: int,
    task: TaskCreate,
    current_user=Depends(get_current_user)
):
    existing_task = await db.task.find_unique(where={"id": task_id})

    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if existing_task.userId != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return await db.task.update(
        where={"id": task_id},
        data={
            "title": task.title,
            "description": task.description
        }
    )

# DELETE


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user=Depends(get_current_user)
):
    existing_task = await db.task.find_unique(where={"id": task_id})

    if not existing_task:
        raise HTTPException(status_code=404, detail="Task not found")

    if existing_task.userId != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.task.delete(where={"id": task_id})

    return {"message": "Task deleted successfully"}

@router.get("/admin/all")
async def get_all_tasks(
    current_user=Depends(require_role("admin"))
):
    return await db.task.find_many()