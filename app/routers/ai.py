from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.task import Task
from app.models.user import User
from app.services.ai_service import generate_tasks_from_prompt
from app.schemas.ai import AITaskRequest
import json

router = APIRouter(prefix="/ai", tags=["AI"])


@router.post("/generate-tasks")
async def generate_tasks(
    request: AITaskRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        # 🔹 Call Ollama
        ai_response = await generate_tasks_from_prompt(request.prompt)

        # 🔹 Parse JSON safely
        tasks_data = json.loads(ai_response)

    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail="AI returned invalid JSON format."
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AI service error: {str(e)}"
        )

    created_tasks = []

    for task in tasks_data:
        new_task = Task(
            title=task.get("title"),
            description=task.get("description"),
            priority=task.get("priority"),
            owner_id=current_user.id
        )
        db.add(new_task)
        created_tasks.append(new_task)

    await db.commit()

    return {
        "message": "Tasks generated successfully",
        "tasks_created": len(created_tasks)
    }