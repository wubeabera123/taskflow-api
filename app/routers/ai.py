from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.task import Task
from app.models.user import User
from app.services.ai_service import generate_tasks_from_prompt
from app.schemas.ai import AITaskRequest
import json
import re

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

        if not ai_response:
            raise HTTPException(
                status_code=500,
                detail="AI returned empty response."
            )

        # 🔹 Clean markdown formatting (```json ... ```)
        cleaned_response = ai_response.strip()
        cleaned_response = re.sub(r"```json|```", "", cleaned_response).strip()

        # 🔹 Parse JSON
        tasks_data = json.loads(cleaned_response)

        # 🔹 Normalize response (handle single object case)
        if isinstance(tasks_data, dict):
            tasks_data = [tasks_data]

        if not isinstance(tasks_data, list):
            raise HTTPException(
                status_code=500,
                detail="AI did not return a valid task list."
            )

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

    # 🔹 Save tasks to DB
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