from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.task import Task
from app.models.user import User
from app.services.ai_service import generate_tasks_from_prompt
from app.schemas.ai import AITaskRequest
from app.schemas.task import TaskResponse

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/generate-tasks", response_model=list[TaskResponse])
async def generate_tasks(
    request: AITaskRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # 🔹 Call AI service (already returns parsed tasks)
        tasks_data = await generate_tasks_from_prompt(request.prompt)

        if not tasks_data:
            raise HTTPException(
                status_code=500,
                detail="AI returned empty task list."
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )

    created_tasks = []

    # 🔹 Save tasks in database
    for task in tasks_data:
        new_task = Task(
            title=task.get("title"),
            description=task.get("description"),
            priority=task.get("priority"),
            is_ai_generated=True,
            ai_prompt=request.prompt,   # ✅ save prompt
            owner_id=current_user.id
        )

        db.add(new_task)
        created_tasks.append(new_task)

    await db.commit()

    # 🔹 Refresh to get IDs
    for task in created_tasks:
        await db.refresh(task)

    # 🔹 Return created tasks
    return created_tasks
