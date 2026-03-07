from pydantic import BaseModel
from typing import List


class AIPriorityRequest(BaseModel):
    tasks: List[str]


class AIPriorityItem(BaseModel):
    task: str
    priority: str


class AIPriorityResponse(BaseModel):
    tasks: List[AIPriorityItem]