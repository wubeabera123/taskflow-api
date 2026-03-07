from pydantic import BaseModel
from typing import List


class AIScheduleRequest(BaseModel):
    task: str
    deadline: str


class AIScheduleItem(BaseModel):
    step: str
    time: str


class AIScheduleResponse(BaseModel):
    schedule: List[AIScheduleItem]