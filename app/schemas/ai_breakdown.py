from pydantic import BaseModel
from typing import List


class AIBreakdownRequest(BaseModel):
    task: str


class AIBreakdownResponse(BaseModel):
    subtasks: List[str]