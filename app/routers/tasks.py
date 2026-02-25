from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.schemas.task import TaskCreate
from app.models.task import Task
from app.dependencies import get_db
from app.core.dependencies import get_current_user, require_role

router = APIRouter(prefix="/tasks", tags=["Tasks"])


# CREATE
@router.post("/")
async def create_task(
    task: TaskCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    new_task = Task(
        title=task.title,
        description=task.description,
        user_id=current_user.id
    )

    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)

    return new_task


# GET ALL (with pagination)
@router.get("/")
async def get_tasks(
    skip: int = 0,
    limit: int = 10,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    total_result = await db.execute(
        select(func.count()).where(Task.user_id == current_user.id)
    )
    total = total_result.scalar()

    result = await db.execute(
        select(Task)
        .where(Task.user_id == current_user.id)
        .order_by(Task.created_at.desc())
        .offset(skip)
        .limit(limit)
    )

    tasks = result.scalars().all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": tasks
    }


# GET ONE
@router.get("/{task_id}")
async def get_task(
    task_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return task


# UPDATE
@router.put("/{task_id}")
async def update_task(
    task_id: int,
    task_data: TaskCreate,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    task.title = task_data.title
    task.description = task_data.description

    await db.commit()
    await db.refresh(task)

    return task


# DELETE
@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalar_one_or_none()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.delete(task)
    await db.commit()

    return {"message": "Task deleted successfully"}


# ADMIN
@router.get("/admin/all")
async def get_all_tasks(
    current_user=Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Task))
    return result.scalars().all()