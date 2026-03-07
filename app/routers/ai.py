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
    """
    Generate tasks using AI and SAVE them to the database.
    """

    try:
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

    # 🔹 Save tasks to database
    for task in tasks_data:
        new_task = Task(
            title=task.get("title"),
            description=task.get("description"),
            priority=task.get("priority"),
            is_ai_generated=True,
            ai_prompt=request.prompt,   # store original AI prompt
            owner_id=current_user.id
        )

        db.add(new_task)
        created_tasks.append(new_task)

    await db.commit()

    # Refresh tasks to get DB IDs
    for task in created_tasks:
        await db.refresh(task)

    return created_tasks


@router.post("/suggest-tasks", response_model=list[TaskResponse])
async def suggest_tasks(
    request: AITaskRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Generate AI task suggestions WITHOUT saving them to the database.
    """

    try:
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

    suggested_tasks = []

    # Convert AI output to TaskResponse objects
    for i, task in enumerate(tasks_data, start=1):
        suggested_tasks.append(
            TaskResponse(
                id=i,  # temporary ID since not saved in DB
                title=task.get("title"),
                description=task.get("description"),
                priority=task.get("priority"),
                is_ai_generated=True
            )
        )

    return suggested_tasks